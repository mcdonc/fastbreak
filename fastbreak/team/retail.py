from csv import DictWriter
from StringIO import StringIO

import colander
import deform

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.url import resource_url
from pyramid.view import view_config

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from substanced.schema import Schema
from substanced.form import FormView

from fastbreak.interfaces import ITeam
from fastbreak.layout import Layout
from fastbreak.utils import parse_whitelist

class TeamView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def subnav_items(self):
        context = self.context
        request = self.request
        items = [
            dict(title='Roster',
                 url=resource_url(context, request)),
            dict(title='Tournaments',
                 url=resource_url(context, request, 'tournaments')),
            dict(title='Contact Info',
                 url=resource_url(context, request, 'contact_info')),
            dict(title='List Email Addresses',
                 url=resource_url(context, request, 'emails')),
            dict(title='Download Roster',
                 url=resource_url(context, request, 'download_roster')),
            #            dict(title='Send Email',
            #                 url=resource_url(context, request, 'email_team')),
            dict(title='Balances',
                 url=resource_url(context, request, 'balances')),
            ]
        return items

    @view_config(renderer='templates/team_view.pt',
                 permission='view',
                 context=ITeam)
    def team_view(self):
        return dict(
            heading=self.context.title + ' Roster',
            team=self.context,
            players=self.context.players(),
            coaches=self.context.coaches(),
            team_managers=self.context.team_managers(),
            )

    @view_config(renderer='templates/team_tournaments.pt',
                 permission='view',
                 name='tournaments',
                 context=ITeam)
    def tournaments_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title
        tourney_names = None

        # TODO Generalize this
        if team_name in ('Blue', 'Orange'):
            tourney_names = ('Southern Lacrosse', 'Nations Cup',
                             'Beach Blast Tourney', 'Beach Blast Camp',
                             'Capital Cup')
        elif team_name in ('White', 'Silver'):
            tourney_names = ('Southern Lacrosse', 'Rock the Field',
                             'Beach Blast Tourney', 'Beach Blast Camp')
        elif team_name in ('Black'):
            tourney_names = ('Southern Lacrosse', 'Sun and Surf')

        for player in self.context.players():
            td = player.tourney_data

        return dict(
            heading=self.context.title + ' Tournaments',
            players=self.context.players(),
            tourney_names=tourney_names
        )

    @view_config(renderer='templates/team_contacts.pt',
                 permission='view',
                 name='contact_info',
                 context=ITeam)
    def contacts_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        return dict(
            heading=self.context.title + ' Contacts',
            players=self.context.players(),
            )

    @view_config(renderer='templates/team_emails.pt',
                 permission='view',
                 name='emails',
                 context=ITeam)
    def emails_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        all_emails = set()
        players = self.context.players()

        for p in players:
            for email in p.all_emails():
                all_emails.add(email)

        joined_comma = ', '.join(all_emails)

        return dict(
            heading=self.context.title + ' Emails',
            players=players,
            joined_comma=joined_comma
        )


    @view_config(renderer='templates/team_balances.pt',
                 permission='view',
                 name='balances',
                 context=ITeam)
    def balances_view(self):
        balances = []
        players = self.context.players()
        for p in players:
            dues = None
            uniform = None
            if p.dues_owed:
                dues = p.dues_owed - p.dues_paid
            if p.uniform_owed:
                uniform = p.uniform_owed - p.uniform_paid
            if not dues and not uniform:
                continue
            balances.append(dict(
                last_name=p.last_name,
                first_name=p.first_name,
                url=self.make_url(self.context),
                dues=dues,
                uniform=uniform
            ))

        return dict(
            heading=self.context.title + ' Emails',
            balances=balances
        )

    @view_config(name='download_roster',
                 permission='view',
                 context=ITeam)
    def download_roster(self):
        fieldnames = ['last_name', 'first_name', 'jersey_number',
                      'primary_email',
                      'parent_last_name', 'parent_first_name']
        output = StringIO()
        writer = DictWriter(output, fieldnames=fieldnames)
        headers = dict((n, n) for n in fieldnames)
        writer.writerow(headers)
        for player in self.context.players():
            g = player.primary_guardian()
            writer.writerow(dict(
                last_name=player.last_name,
                first_name=player.first_name,
                jersey_number=player.jersey_number,
                primary_email=player.primary_email(),
                parent_last_name=g.last_name,
                parent_first_name=g.first_name
            ))

        fn = self.context.title + '_team.csv'
        res = Response(content_type='text/csv', )
        res.content_disposition = 'attachment;filename=%s' % fn
        res.body = output.getvalue()

        return res

# Sending an email
class EmailSchema(Schema):
    to_choices = (
        ('players', 'Players'),
        ('parents', 'Parents'),
        ('coaches', 'Coaches'),
        )
    to_addresses = colander.SchemaNode(
        deform.Set(),
        widget=deform.widget.CheckboxChoiceWidget(values=to_choices)
    )
    from_name = colander.SchemaNode(
        colander.String(),
    )
    from_email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email(),
        )
    subject = colander.SchemaNode(
        colander.String(),
    )
    text = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )


@view_config(
    context=ITeam,
    name='email_team',
    permission='view',
    renderer='fastbreak:templates/form.pt',
    )
class EmailTeamView(FormView, Layout):
    schema = EmailSchema()
    buttons = ('send',)

    @reify
    def subnav_items(self):
        context = self.context
        request = self.request
        items = [
            dict(title='Roster',
                 url=resource_url(context, request)),
            dict(title='Tournaments',
                 url=resource_url(context, request, 'tournaments')),
            dict(title='Contact Info',
                 url=resource_url(context, request, 'contact_info')),
            dict(title='List Email Addresses',
                 url=resource_url(context, request, 'emails')),
            dict(title='Send Email',
                 url=resource_url(context, request, 'email_team')),
            dict(title='Balances',
                 url=resource_url(context, request, 'balances')),
            ]
        return items

    @property
    def heading(self):
        return 'Send Email To ' + self.context.title

    def send_success(self, appstruct):
        whitelist_fn = self.request.registry.settings['whitelist']
        whitelist = parse_whitelist(whitelist_fn)

        settings = self.request.registry.settings
        use_queue = settings.get('mail.queue_path', None)

        # Build up address list

        for r in appstruct['to_addresses']:
            if r not in whitelist:
                print r, "not on whitelist, skipping"
                continue
            sender = '"%s" <%s>' % (
                appstruct['from_name'], appstruct['from_email']
                )
            message = Message(
                sender=sender,
                subject=appstruct['subject'],
                recipients=[r],
                html=appstruct['text']
            )
            mailer = get_mailer(request)
            if use_queue:
                mailer.send_to_queue(message)

        url = self.request.resource_url(self.context)
        return HTTPFound(location=url)

