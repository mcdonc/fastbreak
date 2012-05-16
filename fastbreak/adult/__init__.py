import colander
from deform.widget import TextAreaWidget
from persistent import Persistent

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import (
    IAdult
    )
from fastbreak.utils import BaseContent

class AdultSchema(Schema):
    first_name = colander.SchemaNode(
        colander.String(),
    )
    last_name = colander.SchemaNode(
        colander.String(),
    )
    nickname = colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        )
    email = colander.SchemaNode(
        colander.String(),
    )
    additional_emails = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    home_phone = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    mobile_phone = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    address1 = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    address2 = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    city = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    state = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    zip = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    note = colander.SchemaNode(
        colander.String(),
        widget=TextAreaWidget(rows=10, cols=60),
        missing=colander.null
    )
    la_id = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )


class AdultBasicPropertySheet(PropertySheet):
    schema = AdultSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        return dict(
            name=context.__name__,
            first_name=context.first_name,
            last_name=context.last_name,
            nickname=context.nickname,
            email=context.email,
            additional_emails=context.additional_emails,
            home_phone=context.home_phone,
            mobile_phone=context.mobile_phone,
            address1=context.address1,
            address2=context.address2,
            city=context.city,
            state=context.state,
            zip=context.zip,
            note=context.note,
            la_id=context.la_id,
            )

    def set(self, struct):
        context = self.context
        context.first_name = struct['first_name']
        context.last_name = struct['last_name']
        context.nickname = struct['nickname']
        context.email = struct['email']
        context.additional_emails = struct['additional_emails']
        context.home_phone = struct['home_phone']
        context.mobile_phone = struct['mobile_phone']
        context.address1 = struct['address1']
        context.address2 = struct['address2']
        context.city = struct['city']
        context.state = struct['state']
        context.zip = struct['zip']
        context.note = struct['note']
        context.la_id = struct['la_id']


@content(
    IAdult,
    name='Adult',
    icon='icon-align-left',
    add_view='add_adult',
    propertysheets=(
        ('Basic', AdultBasicPropertySheet),
        ),
    catalog=True,
    )
class Adult(BaseContent):
    def __init__(self, first_name, last_name, nickname, email,
                 additional_emails, home_phone, mobile_phone,
                 address1, address2, city, state, zip,
                 note, la_id
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.email = email
        self.additional_emails = additional_emails
        self.home_phone = home_phone
        self.mobile_phone = mobile_phone
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        self.note = note
        self.la_id = la_id

    @property
    def title(self):
        return ' '.join((self.last_name, self.first_name))

    def texts(self): # for indexing
        nickname = self.nickname
        if self.nickname is colander.null:
            nickname = ''
        t = ' '.join([self.first_name, self.last_name, nickname])
        return t
