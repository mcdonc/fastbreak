import colander
from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.service import find_service
from substanced.site import ISite

from fastbreak.migration import Migration
from fastbreak.utils import make_name

from fastbreak.interfaces import (
    ITeam,
    IProgram,
    IAdult,
    IPlayer
    )
from fastbreak.adult import AdultBasicPropertySheet
from fastbreak.player import PlayerBasicPropertySheet
from fastbreak.program import ProgramBasicPropertySheet
from fastbreak.team import TeamBasicPropertySheet


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
    buttons = ('import',)

    def import_success(self, appstruct):
        root = self.request.root
        registry = self.request.registry
        import_dir = registry.settings['import_dir']
        objectmap = find_service(self.context, 'objectmap')

        # First add STORM as a program
        appstruct = dict(title='STORM')
        storm = registry.content.create(IProgram, **appstruct)
        root['storm'] = storm
        propsheet = ProgramBasicPropertySheet(storm, self.request)
        propsheet.set(appstruct)

        m = Migration(self.context, self.request)

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
                root[name] = person
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
        for id, p in m.players.items():
            first_name = p['first_name']
            last_name = p['last_name']
            email = p['email']

            # TODO split this up and put on additional emails
            additional_emails = colander.null

            mobile_phone = p['mobile_phone']
            uslax = p['uslax']
            if p['is_goalie'] == 'TRUE':
                is_goalie = True
            else:
                is_goalie = False
            if p['grade'] == '':
                grade = colander.null
            else:
                grade = int(p['grade'])
            grade = p['grade']
            school = p['school']
            if p['jersey_number'] == '':
                jersey_number = colander.null
            else:
                jersey_number = int(p['jersey_number'])
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
            root[player_name] = player
            propsheet = PlayerBasicPropertySheet(player,
                                                 self.request)
            propsheet.set(appstruct)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))

