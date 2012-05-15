import colander
from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.service import find_service
from substanced.site import ISite

from fastbreak.migration import Migration
from fastbreak.utils import (
    make_name,
    sample_data
    )

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
            head_coach = p['primary_coach_ref']
            assistant_coach = p['coach_ref']
            team_manager = p['manager_ref']

            if head_coach != '' or assistant_coach != '' or\
               team_manager != '' or id in m.guardian_ids:
                first_name = p['first_name']
                last_name = p['last_name']
                title = last_name + ' ' + first_name
                name = make_name(title)
                appstruct = dict(title=title)
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

            # Some references
            team_name = p['team_ref']
            team_oid = objectmap.objectid_for(all_teams[team_name])
            guardian_ref = int(p['guardian_ref'])
            guardian = all_guardians[guardian_ref]
            guardian_oid = objectmap.objectid_for(guardian)
            print "guardian_oid", guardian_oid

            appstruct = dict(
                first_name=first_name,
                last_name=last_name,
                nickname='',
                team=team_oid,
                primary_guardian=guardian_oid,
                other_guardian=colander.null
            )
            player = registry.content.create(IPlayer,
                                             **appstruct)
            player_name = make_name(last_name + ' ' + first_name)
            root[player_name] = player
            propsheet = PlayerBasicPropertySheet(player,
                                                 self.request)
            propsheet.set(appstruct)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))


    def import_success_old(self, appstruct):
        root = self.request.root
        registry = self.request.registry
        import_dir = registry.settings['import_dir']
        objectmap = find_service(self.context, 'objectmap')

        m = Migration(import_dir)
        for team in ('Blue', 'Orange', 'White', 'Black', 'Silver'):
            name = make_name(team_title)
            appstruct = dict(
                title=team_title,
                head_coach=hc_oid,
                assistant_coach=ac_oid,
                team_manager=tm_oid)
            team = registry.content.create(ITeam, **appstruct)
            storm[name] = team
            propsheet = TeamBasicPropertySheet(team, self.request)
            propsheet.set(appstruct)
            team_oid = objectmap.objectid_for(team)


        # First add STORM as a program
        appstruct = dict(title='STORM')
        storm = registry.content.create(IProgram, **appstruct)
        root['storm'] = storm
        propsheet = ProgramBasicPropertySheet(storm, self.request)
        propsheet.set(appstruct)





        # Add some Teams and families
        for team_title, team_data in sample_data.items():
            # Head coach
            hc_title = team_data['head_coach']
            hc_name = make_name(hc_title)
            appstruct = dict(title=hc_title)
            hc_adult = registry.content.create(IAdult,
                                               **appstruct)
            root[hc_name] = hc_adult
            propsheet = AdultBasicPropertySheet(hc_adult,
                                                self.request)
            propsheet.set(appstruct)
            hc_oid = objectmap.objectid_for(hc_adult)

            # Assistant coach
            ac_title = team_data['assistant_coach']
            ac_name = make_name(ac_title)
            appstruct = dict(title=ac_title)
            ac_adult = registry.content.create(IAdult,
                                               **appstruct)
            root[ac_name] = ac_adult
            propsheet = AdultBasicPropertySheet(ac_adult,
                                                self.request)
            propsheet.set(appstruct)
            ac_oid = objectmap.objectid_for(ac_adult)

            # Team Manager
            tm_title = team_data['team_manager']
            tm_name = make_name(tm_title)
            appstruct = dict(title=tm_title)
            tm_adult = registry.content.create(IAdult,
                                               **appstruct)
            root[tm_name] = tm_adult
            propsheet = AdultBasicPropertySheet(tm_adult,
                                                self.request)
            propsheet.set(appstruct)
            tm_oid = objectmap.objectid_for(tm_adult)

            # Make a team
            name = make_name(team_title)
            appstruct = dict(
                title=team_title,
                head_coach=hc_oid,
                assistant_coach=ac_oid,
                team_manager=tm_oid)
            team = registry.content.create(ITeam, **appstruct)
            storm[name] = team
            propsheet = TeamBasicPropertySheet(team, self.request)
            propsheet.set(appstruct)
            team_oid = objectmap.objectid_for(team)

            # Make values for each family
            for family in team_data['families']:
                # Primary guardian
                primary_title = family[0]
                primary_name = make_name(primary_title)
                appstruct = dict(title=primary_title)
                primary_adult = registry.content.create(IAdult,
                                                        **appstruct)
                root[primary_name] = primary_adult
                propsheet = AdultBasicPropertySheet(primary_adult,
                                                    self.request)
                propsheet.set(appstruct)
                primary_oid = objectmap.objectid_for(primary_adult)

                # Other guardian
                other_title = family[1]
                other_name = make_name(other_title)
                appstruct = dict(title=other_title)
                other_adult = registry.content.create(IAdult,
                                                      **appstruct)
                root[other_name] = other_adult
                propsheet = AdultBasicPropertySheet(other_adult,
                                                    self.request)
                propsheet.set(appstruct)
                other_oid = objectmap.objectid_for(other_adult)

                # Player
                player_title = family[2]
                player_fn, player_ln = player_title.split(' ')
                player_nickname = 'Peanut'
                player_name = make_name(player_title)
                appstruct = dict(
                    first_name=player_fn,
                    last_name=player_ln,
                    nickname=player_nickname,
                    team=team_oid,
                    primary_guardian=primary_oid,
                    other_guardian=other_oid
                )
                player = registry.content.create(IPlayer,
                                                 **appstruct)
                root[player_name] = player
                propsheet = PlayerBasicPropertySheet(player,
                                                     self.request)
                propsheet.set(appstruct)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))
