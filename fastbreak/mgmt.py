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
from fastbreak.adult import AdultBasicPropertySheet
from fastbreak.gspread_sync import GDocSync
from fastbreak.player import PlayerBasicPropertySheet
from fastbreak.program import ProgramBasicPropertySheet
from fastbreak.team import TeamBasicPropertySheet
from fastbreak.signup import SignupBasicPropertySheet


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
    buttons = ('import', 'sync', 'init_players', 'sync_players')

    def find_la_id(self, la_id):
        """Find the resource matching a LeagueAthletics ID"""
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(
            la_id=(la_id,),
            )
        result = [resolver(docid) for docid in docids][0]

        return result

    def init_players_success(self, appstruct):
        g = GDocSync()

        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(
            interfaces=(IPlayer,),
            sort_index=('title'),
            )
        players = [resolver(docid) for docid in docids]

        g.init_players(players)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

    def sync_players_success(self, appstruct):
        g = GDocSync()
        g.append_people('players')

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

    def sync_success(self, appstruct):
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
                for k,v in row.items():
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
            jersey_number=p['jersey_number']
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

