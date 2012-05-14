import colander
from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.service import find_service
from substanced.site import ISite

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
        objectmap = find_service(self.context, 'objectmap')

        # First add STORM as a program
        name = u'storm'
        appstruct = dict(title='STORM')
        storm = registry.content.create(IProgram, **appstruct)
        root[name] = storm
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

            # Make a team
            name = make_name(team_title)
            appstruct = dict(
                title=team_title,
                head_coach=hc_oid)
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
                player_name = make_name(player_title)
                appstruct = dict(
                    title=player_title,
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
