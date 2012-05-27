import colander
from persistent.mapping import PersistentMapping
from pyramid.httpexceptions import HTTPFound

from substanced.folder import IFolder
from substanced.form import FormView
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.service import find_service
from substanced.site import ISite

from fastbreak.migration import (
    Migration,
    regs
    )
from fastbreak.utils import make_name

from fastbreak.interfaces import (
    ITeam,
    IProgram,
    IAdult,
    IPlayer,
    IRegistration,
    ISignup
    )
from fastbreak.adult import (
    AdultSchema,
    AdultBasicPropertySheet
    )
from fastbreak.gspread_sync import GDocSync
from fastbreak.player import (
    PlayerSchema,
    PlayerBasicPropertySheet
    )
from fastbreak.program import ProgramBasicPropertySheet
from fastbreak.team import TeamBasicPropertySheet
from fastbreak.signup import SignupBasicPropertySheet


@mgmt_view(
    context=ISite,
    name='gsync_data',
    tab_title='GSpread Sync',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    )
class GspreadSyncView(FormView):
    title = 'GSpread Sync'
    schema = Schema()
    buttons = ('init_adults', 'init_players')

    def init_players_success(self, appstruct):
        g = GDocSync()

        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(
            interfaces=(IPlayer,),
            sort_index=('title'),
            )
        players = [resolver(docid) for docid in docids]

        g.init_resources('players', PlayerSchema, players)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

    def init_adults_success(self, appstruct):
        g = GDocSync()

        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(
            interfaces=(IAdult,),
            sort_index=('title'),
            )
        adults = [resolver(docid) for docid in docids]

        g.init_resources('adults', AdultSchema, adults)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))


@mgmt_view(
    context=ISite,
    name='import_data',
    tab_title='Import Data',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    )
class ImportDataView(FormView):
    title = 'Import Data'
    schema = Schema()
    buttons = ('sync_teams', 'import',
               'sync_adults', 'sync_players', 'sync_tourneys')

    def find_la_id(self, la_id):
        """Find the resource matching a LeagueAthletics ID"""
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(
            la_id=(la_id,),
        )
        result = [resolver(docid) for docid in docids][0]

        return result

    def unserialize(self, field_value):
        # TODO drive this with the actual schema rather than hardwire

        if field_value == 'None':
            return colander.null

        return field_value

    def make_storm_and_people(self):
        """If storm and people aren't in root, make them and return"""

        registry = self.request.registry
        root = self.request.root

        try:
            people = root['people']
        except KeyError:
            # Doesn't exist, let's make it
            appstruct = dict(title='People')
            people = registry.content.create(IFolder)
            root['people'] = people

        try:
            storm = root['storm']
        except:
            appstruct = dict(title='STORM')
            storm = registry.content.create(IProgram, **appstruct)
            root['storm'] = storm

        return people, storm


    def sync_teams_success(self, appstruct):
        # Read data from GSpread. If an adult doesn't exist,
        # create them. If an adult does exist, update them.

        registry = self.request.registry

        people, storm = self.make_storm_and_people()

        g = GDocSync()
        rows = g.get_rows('setup', ['Teams', ])['Teams']

        # Load the data, but not content, for some teams
        for row in rows:
            appstruct = dict(
                title=row['title'],
            )
            team = registry.content.create(ITeam, **appstruct)
            name = row['title'].lower()
            storm[name] = team

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))


    def sync_adults_success(self, appstruct):
        # Read data from GSpread. If an adult doesn't exist,
        # create them. If an adult does exist, update them.

        registry = self.request.registry
        objectmap = find_service(self.context, 'objectmap')

        people, storm = self.make_storm_and_people()

        g = GDocSync()
        rows = g.get_rows('adults', ['Sheet1', ])['Sheet1']

        for p in rows:
            name = make_name(p['first_name'] + ' ' + p['last_name'])
            appstruct = dict(
                first_name=p['first_name'],
                last_name=p['last_name'],
                nickname=p['nickname'],
                email=p['email'],
                additional_emails=p['additional_emails'],
                home_phone=p['home_phone'],
                mobile_phone=p['mobile_phone'],
                address1=p['address1'],
                address2=p['address2'],
                city=p['city'],
                state=p['state'],
                zip=p['zip'],
                note=p['note'],
                la_id=p['la_id']
            )
            # Do we already have a player? If not, create one
            try:
                person = self.find_la_id(p['la_id'])
                person.update(appstruct)
            except IndexError:
                person = registry.content.create(IAdult,
                                                 **appstruct)
                people[name] = person

        # Now that we have made the adults, we can wire up the coaches
        # and team managers for each team, using the la_id.
        g = GDocSync()
        rows = g.get_rows('setup', ['Teams', ])['Teams']
        for row in rows:
            coaches = set()
            team_managers = set()
            team_name = row['name']
            for la_id in str(row['coaches']).strip().split(';'):
                if la_id is '':
                    continue
                la_id = int(la_id.strip())
                coach = self.find_la_id(la_id)
                oid = objectmap.objectid_for(coach)
                coaches.add(oid)
            for la_id in str(row['team_managers']).strip().split(';'):
                if la_id is '':
                    continue
                la_id = int(la_id.strip())
                tm = self.find_la_id(la_id)
                oid = objectmap.objectid_for(tm)
                team_managers.add(oid)
            appstruct = dict(
                coaches=coaches, team_managers=team_managers
            )
            team = storm[team_name]
            team.connect_all(appstruct)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))


    def sync_players_success(self, appstruct):
        # Read data from GSpread. If a player doesn't exist,
        # create them. If a player does exist, update them.

        registry = self.request.registry
        objectmap = find_service(self.context, 'objectmap')
        storm_teams = self.request.root['storm']
        people = self.request.root['people']

        g = GDocSync()
        rows = g.get_rows('players', ['Sheet1', ])['Sheet1']

        for p in rows:
            appstruct = dict(
                first_name=p['first_name'],
                last_name=p['last_name'],
                dues_paid=self.unserialize(p['dues_paid']),
                uniform_paid=self.unserialize(p['uniform_paid']),
                note=p['note'],
                nickname=p['nickname'],
                email=p['email'],
                additional_emails=p['additional_emails'],
                mobile_phone=p['mobile_phone'],
                uslax=self.unserialize(p['uslax']),
                is_goalie=self.unserialize(p['is_goalie']),
                grade=self.unserialize(p['grade']),
                school=p['school'],
                jersey_number=self.unserialize(p['jersey_number']),
                la_id=p['la_id']
            )

            # Do we already have a player? If not, create one
            try:
                player = self.find_la_id(p['la_id'])
                player.update(appstruct)
            except IndexError:
                # We don't have one, so make one
                player = registry.content.create(IPlayer,
                                                 **appstruct)
                player_name = make_name(p['first_name'] + ' ' +\
                                        p['last_name'])
                people[player_name] = player

            # Connect references
            # TODO fix guardian ref of 1431127 for Austin Woods
            team_name = p['teams'].strip()
            team = storm_teams[team_name]
            team_oid = objectmap.objectid_for(team)
            primary_guardian_la_id = int(p['primary_guardian'])
            primary_guardian_oid = objectmap.objectid_for(
                self.find_la_id(primary_guardian_la_id)
            )
            player.connect_all(dict(
                teams=[team_oid],
                primary_guardian=primary_guardian_oid,
                other_guardians=[]
            ))

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

    def sync_tourneys_success(self, appstruct):
        g = GDocSync()

        results = g.get_rows('tourneys',
            ('Blue', 'Orange', 'White', 'Black', 'Silver'))

        # Iterate over spreadsheet results for each player and update
        # player.tourney_data
        for team in results.values():
            for row in team:
                la_id = int(row['ID'])
                player = self.find_la_id(la_id)
                player.tourney_data = PersistentMapping()
                for k, v in row.items():
                    # Strip whitespace off spreadsheet data
                    try:
                        player.tourney_data[k.strip()] = v.strip()
                    except AttributeError:
                        # Must not be an int
                        player.tourney_data[k] = v

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

    def import_success(self, appstruct):
        root = self.request.root
        registry = self.request.registry
        objectmap = find_service(self.context, 'objectmap')

        people, storm = self.make_storm_and_people()

        # Import data, but not create content, for players/adults
        m = Migration(self.context, self.request)
        m.load_players()
        m.load_adults()

        # Adults
        for la_id, p in m.adults.items():
            # Skip duplicate adults in the stupid CSV file. Only import
            # adults who are referenced as a guardian.
            # TODO: Make sure we pick up other_guardians as well

            head_coach = p['primary_coach_ref'].strip()
            assistant_coach = p['coach_ref'].strip()
            team_manager = p['manager_ref'].strip()

            is_leadership = (head_coach != '') or\
                            (assistant_coach != '') or\
                            (team_manager != '')

            if la_id not in m.guardian_ids and not is_leadership:
                continue
            appstruct = dict(
                first_name=p['first_name'],
                last_name=p['last_name'],
                nickname='',
                email=p['email'],
                additional_emails=colander.null,
                home_phone=p['home_phone'],
                mobile_phone=p['mobile_phone'],
                address1=p['address_1'],
                address2=p['address_2'],
                city=p['city'],
                state=p['state'],
                zip=p['zip'],
                note=p['note'],
                la_id=la_id
            )
            title = p['first_name'] + ' ' + p['last_name']
            name = make_name(title)
            person = registry.content.create(IAdult,
                                             **appstruct)
            people[name] = person

        # Players
        for la_id, p in m.players.items():
            appstruct = dict(
                first_name=p['first_name'],
                last_name=p['last_name'],
                nickname='',
                email=p['email'],
                additional_emails=colander.null,
                mobile_phone=p['mobile_phone'],
                note=p['note'],
                uslax=p['uslax'],
                is_goalie=p['is_goalie'],
                grade=p['grade'],
                school=p['school'],
                jersey_number=p['jersey_number'],
                la_id=la_id,
                dues_paid=colander.null,
                uniform_paid=colander.null
            )
            title = p['first_name'] + ' ' + p['last_name']
            name = make_name(title)
            player = registry.content.create(IPlayer,
                                             **appstruct)
            people[name] = player

            # Make some connections
            team_name = p['team_ref'].lower()
            team = storm[team_name]
            team = objectmap.objectid_for(team)
            guardian_ref = int(p['guardian_ref'])
            pg = self.find_la_id(guardian_ref)
            primary_guardian_oid = objectmap.objectid_for(pg)
            player.connect_all(dict(
                teams=[team, ],
                primary_guardian=primary_guardian_oid,
                other_guardians=[colander.null, ]
            ))

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))


    ######








    def xxx_import_success(self, appstruct):
        root = self.request.root
        registry = self.request.registry
        objectmap = find_service(self.context, 'objectmap')

        # First add STORM as a program
        appstruct = dict(title='STORM')
        storm = registry.content.create(IProgram, **appstruct)
        root['storm'] = storm
        propsheet = ProgramBasicPropertySheet(storm, self.request)
        propsheet.set(appstruct)

        # A People folder
        appstruct = dict(title='People')
        people = registry.content.create(IFolder)
        root['people'] = people

        m = Migration(self.context, self.request)

        # Make some Registrations
        for short_name, reg in regs.items():
            appstruct = dict(
                title=reg.title,
                cost=reg.cost
            )
            registration = registry.content.create(IRegistration,
                                                   **appstruct)
            storm[reg.name] = registration
            reg.content = registration

        # Load the data, but not content, for some teams
        all_teams = {}
        for title in ('Blue', 'Orange', 'White', 'Black', 'Silver'):
            appstruct = dict(
                title=title,
                head_coach=colander.null,
                assistant_coach=colander.null,
                team_manager=colander.null,
                )
            team = registry.content.create(ITeam, **appstruct)
            storm[title.lower()] = team
            propsheet = TeamBasicPropertySheet(team, self.request)
            propsheet.set(appstruct)
            all_teams[title.lower()] = team


        # Import data, but not create content, for players/adults
        m.load_players()
        m.load_adults()

        # Add adults
        gids = m.guardian_ids.keys()
        all_guardians = {}
        for id, p in m.adults.items():
            # Data
            first_name = p['first_name']
            last_name = p['last_name']
            email = p['email']

            # TODO split this up and put on additional emails
            additional_emails = colander.null
            home_phone = p['home_phone']
            mobile_phone = p['mobile_phone']
            address1 = p['address_1']
            address2 = p['address_2']
            city = p['city']
            state = p['state']
            zip = p['zip']
            note = colander.null
            la_id = id

            # References
            head_coach = p['primary_coach_ref']
            assistant_coach = p['coach_ref']
            team_manager = p['manager_ref']

            if head_coach != '' or assistant_coach != '' or\
               team_manager != '' or id in m.guardian_ids:
                first_name = p['first_name']
                last_name = p['last_name']
                title = first_name + ' ' + last_name
                name = make_name(title)
                appstruct = dict(
                    first_name=first_name,
                    last_name=last_name,
                    nickname='',
                    email=email,
                    additional_emails=additional_emails,
                    home_phone=home_phone,
                    mobile_phone=mobile_phone,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    zip=zip,
                    note=note,
                    la_id=la_id

                )
                person = registry.content.create(IAdult,
                                                 **appstruct)
                people[name] = person
                propsheet = AdultBasicPropertySheet(person, self.request)
                propsheet.set(appstruct)

                # Keep track of this for later on in players
                all_guardians[id] = person

                # Hook up roles
                if head_coach != '':
                    t = all_teams[head_coach]
                    t.connect_head_coach(person)
                if assistant_coach != '':
                    t = all_teams[assistant_coach]
                    t.connect_assistant_coach(person)
                if team_manager != '':
                    t = all_teams[team_manager]
                    t.connect_team_manager(person)

        # Add players
        la_players = {}
        for id, p in m.players.items():
            first_name = p['first_name']
            last_name = p['last_name']
            email = p['email']

            # TODO split this up and put on additional emails
            additional_emails = colander.null

            mobile_phone = p['mobile_phone']
            uslax = p['uslax']
            is_goalie = p['is_goalie']
            grade = p['grade']
            school = p['school']
            jersey_number = p['jersey_number']
            note = colander.null
            la_id = id


            # Some references
            team_name = p['team_ref']
            team_oid = objectmap.objectid_for(all_teams[team_name])
            guardian_ref = int(p['guardian_ref'])
            guardian = all_guardians[guardian_ref]
            guardian_oid = objectmap.objectid_for(guardian)

            appstruct = dict(
                first_name=first_name,
                last_name=last_name,
                nickname='',
                email=email,
                additional_emails=additional_emails,
                mobile_phone=mobile_phone,
                uslax=uslax,
                is_goalie=is_goalie,
                grade=grade,
                school=school,
                jersey_number=jersey_number,

                # References
                team=team_oid,
                primary_guardian=guardian_oid,
                other_guardian=colander.null,

                # Remainder
                note=note,
                la_id=la_id
            )
            player = registry.content.create(IPlayer,
                                             **appstruct)
            player_name = make_name(first_name + ' ' + last_name)
            people[player_name] = player
            propsheet = PlayerBasicPropertySheet(player,
                                                 self.request)
            propsheet.set(appstruct)
            la_players[la_id] = player

        # Now make Signup instances for each Player's stuff
        m.load_registrations()
        for s in m.signups:
            player = la_players[s['player_ref']]
            registration = storm[s['event_ref']]
            title = player.first_name + ' ' + player.last_name

            appstruct = dict(
                status=s['status'],
                title=title,
                note='',
                player=player,
                )
            signup = registry.content.create(ISignup, **appstruct)
            registration[make_name(title)] = signup
            propsheet = SignupBasicPropertySheet(signup, self.request)
            propsheet.set(appstruct)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

