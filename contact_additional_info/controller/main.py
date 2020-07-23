# -*- coding: utf-8 -*-
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime, date
import locale
import logging

_logger = logging.getLogger("_name_")

class BuyersAccountPortal(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["mobile", "email", "street2","zipcode", "company_type"]
    OPTIONAL_BILLING_FIELDS = ["buyer_relationship_id", "current_relationship", "state_id", "vat", "company_name", "city", "phone", "middle_name", "suffix_name", "phone", "home_number", "street", "country_id"]

    def get_barangay(self, zip):
        return request.env['res.barangay'].sudo().search([('zip_code', '=', zip)], limit=1)

    def details_form_validate(self, data):
        error = dict()
        error_message = []
        _logger.info('\n\n\nRequired Fields\n')
        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                _logger.info(f'{field_name}: {data.get(field_name)}\n')
                error[field_name] = 'missing'
        _logger.info('\n\n\n')
        partner = request.env.user.partner_id
        #Business Address Zipcode Validation
        if data.get('business_zipcode') and data.get('business_country_id') == 176:
            barangay = self.get_barangay(data.get('business_zipcode'))
            if not barangay[:1]:
                error["email"] = 'error'
                error_message.append(_('Invalid Business Address Zip Code! cannot found in the Zipcode Philippinese directories.\n Please enter a valid Zip Code.'))

        #Work Address Zipcode Validation
        if data.get('emp_zipcode') and data.get('emp_country_id') == 176:
            barangay = self.get_barangay(data.get('emp_zipcode'))
            if not barangay[:1]:
                error["email"] = 'error'
                error_message.append(_('Invalid Employement Address Zip Code! cannot found in the Zipcode Philippinese directories.\n Please enter a valid Zip Code.'))


        #Partner Zipcode Validation
        if data.get('zipcode'):
            barangay = self.get_barangay(data.get('zipcode'))
            if not barangay[:1]:
                error["email"] = 'error'
                error_message.append(_('Invalid Contact Address Zip Code! cannot found in the Zipcode Philippinese directories.\n Please enter a valid Zip Code.'))

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation

        if data.get("vat") and partner and partner.vat != data.get("vat"):
            if partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    if data.get("country_id"):
                        data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")), data.get("vat"))
                    partner_dummy = partner.new({
                        'vat': data['vat'],
                        'country_id': (int(data['country_id'])
                                       if data.get('country_id') else False),
                    })
                    try:
                        partner_dummy.check_vat()
                    except ValidationError:
                        error["vat"] = 'error'
            else:
                error_message.append(_('Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        # error message for empty required fields
        try:
            if [err for err in error.values() if err == 'missing']:
                error_message.append(_('Some required fields are empty.'))
        except:
            pass
        unknown = [k for k in data if k not in self.MANDATORY_BILLING_FIELDS + self.OPTIONAL_BILLING_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message

    def validate_mandatory_optional_fields(self, post):
        self.OPTIONAL_BILLING_FIELDS += ['id','name', 'business_street','salary_income',
                                         'business_street2', 'emp_company_name', 'emp_street',
                                         'emp_street2', 'other_income','business_name',
                                         'business_zipcode','emp_zipcode', "civil_status",
                                         "educational_attainment", "dob", "dependents", "house_type", "employment_status", "dob",
                                         "firstname", "lastname", "gender", "nationality_country_id"
                                         ]
        # if post.get('company_type') == 'person':
        #     self.MANDATORY_BILLING_FIELDS += ["firstname", "lastname", "gender", "nationality_country_id"]
        #     self.OPTIONAL_BILLING_FIELDS += ['name']
        # else:
        #     self.OPTIONAL_BILLING_FIELDS += ["firstname", "lastname", "gender", "civil_status", "nationality_country_id", "educational_attainment", "dob", "dependents", "house_type", "employment_status"]
        #     self.MANDATORY_BILLING_FIELDS += ['name']
        if post.get('business_name'):
            self.MANDATORY_BILLING_FIELDS += ["business_industry", "business_type", "establishment_date", "business_country_id", "business_region", "business_city"]
        else:
            self.OPTIONAL_BILLING_FIELDS += ["business_industry", "business_type", "establishment_date", "business_country_id", "business_region", "business_city"]
        if post.get('emp_company_name'):
            self.MANDATORY_BILLING_FIELDS += ['emp_industry_id', 'emp_contract_status', 'emp_position_level', 'employment_date', 'emp_country_id', 'emp_region', 'emp_city', 'salary_income']
        else:
            self.OPTIONAL_BILLING_FIELDS += ['emp_industry_id', 'emp_contract_status', 'emp_position_level', 'employment_date', 'emp_country_id', 'emp_region', 'emp_city']
        for count in range(1, 5):
            self.OPTIONAL_BILLING_FIELDS += [f'credit_card_holder{count}', f'credit_card_id{count}']
            if post.get(f'credit_card_holder{count}'):
                self.MANDATORY_BILLING_FIELDS += [f'credit_card_name{count}']
            else:
                self.OPTIONAL_BILLING_FIELDS += [f'credit_card_name{count}']
        for count in range(1, 5):
            self.OPTIONAL_BILLING_FIELDS += [f'loan_id{count}', f'loan_amortization{count}']
            if post.get(f'loan_amortization{count}') and post.get(f'loan_amortization{count}') != 0:
                self.MANDATORY_BILLING_FIELDS += [f'loan_institution{count}', f'loan_type{count}', f'loan_granted{count}', f'loan_maturity{count}']
            else:
                self.OPTIONAL_BILLING_FIELDS += [f'loan_institution{count}', f'loan_type{count}', f'loan_granted{count}', f'loan_maturity{count}']
        for count in range(1, 5):
            self.OPTIONAL_BILLING_FIELDS += [f'contact_reference_id{count}', f'contact_reference_name{count}',f'contact_reference_other{count}']
            if post.get(f'contact_reference_name{count}'):
                self.MANDATORY_BILLING_FIELDS += [f'contact_reference_relationship{count}', f'contact_reference_address{count}', f'contact_reference_contact_number{count}']
            else:
                self.OPTIONAL_BILLING_FIELDS += [f'contact_reference_relationship{count}', f'contact_reference_address{count}', f'contact_reference_contact_number{count}']

    def process_business_data(self, partner, business, data):
        if data[0]:
            business_data = {
                'name': data[0],
                'industry_id': data[1] or 0,
                'business_type': data[2],
                'establishment_date': data[3],
                'street': data[8],
                'street2': data[9],
                'zip': data[5],
                'country_id': data[4],
            }
            if data[4] == 176: #Philippines
                business_barangay = self.get_barangay(data[5])
                business_data.update({
                    'barangay_id': business_barangay.id,
                    'city_id': business_barangay.city_id.id,
                    'city': f"{business_barangay.name}, {business_barangay.city_id.name}",
                    'region':f"{business_barangay.province_id.name}, {business_barangay.state_id.name}",
                    'province_id': business_barangay.province_id.id,
                    'state_id': business_barangay.state_id.id,
                    'island_group_id': business_barangay.island_group_id.id,
                    'continent_region_id': business_barangay.continent_region_id.id,
                    'continent_id': business_barangay.continent_id.id,
                })
            else:
                business_data.update({
                    'city': data[6],
                    'region': data[7]
                })
            if business[:1]:
                business.sudo().write(business_data)
            else:
                business_data['partner_id'] = partner.id
                request.env['res.partner.business'].sudo().create(business_data)

    def process_loan(self, partner, data):
        loan = request.env['res.partner.loan']
        loan_data = {
            'name': data[1],
            'type_of_loan': data[2],
            'date_paid': data[3],
            'maturity_date': data[4],
            'monthly_amortization': data[5] and locale.atof(data[5]) or 0
        }
        if data[0]:
            rec = loan.sudo().browse(data[0])
            if (data[5] and locale.atof(data[5])) <= 0 or not data[1]:
                loan_data['name'] = "Unsupplied Data"
            rec.sudo().write(loan_data)
        else:
            if data[1]:
                loan_data['partner_id'] = partner.id
                loan.sudo().create(loan_data)

    def process_credit_card(self, partner, data):
        card = request.env['res.partner.credit.card.issuer']
        card_data = {
            'name': data[1],
            'card_holder_name': data[2]
        }
        if data[0]:
            rec = card.sudo().browse(data[0])
            if not data[1]:
                card_data['name'] = "Unsupplied Data"
            rec.sudo().write(card_data)
        else:
            if data[1]:
                card_data['partner_id'] = partner.id
                card.sudo().create(card_data)

    def process_contact_reference(self, partner, data):
        contact_reference = request.env['res.partner.personal.references']
        contact_data = {
            'name': data[1],
            'buyer_relationship': data[2],
            'contact_number': data[3],
            'address': data[4],
            'other': data[5]
        }
        if data[0]:
            rec = contact_reference.sudo().browse(data[0])
            # if not data[1]:
            #     rec.sudo().unlink()
            # else: rec.sudo().write(contact_data)
            if not data[1]:
                contact_data['name'] = "Unsupplied Data"
            rec.sudo().write(contact_data)
        else:
            if data[1]:
                contact_data['partner_id'] = partner.id
                contact_reference.sudo().create(contact_data)

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        _logger.info(f'\n\nGet Post: {post}\n\n\n')
        values = self._prepare_portal_layout_values()
        id = False
        action = False
        company_type = 'person'
        partner = request.env.user.partner_id
        if (post.get('action') and post.get('action') in ['edit_spuase', 'edit_co-borrower', 'edit_attorney-in-fact']) and post.get('id'):
            partner = request.env['res.partner'].sudo().browse(int(post.get('id')))
            id = post.pop('id')
            action = post.pop('action')
        elif post.get('action'):
            action = post.pop('action')
            partner = False
        if partner:
            company_type = partner.company_type
        if not post.get('country_id'):
            post['country_id'] = request.env.user.partner_id.country_id.id
        buyer_relationship = 'buyer_relationship_id' in post and post.pop('buyer_relationship_id') or False
        current_relationship = 'current_relationship' in post and post.pop('current_relationship') or False
        if current_relationship and not buyer_relationship:
            buyer_relationship = current_relationship
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            self.validate_mandatory_optional_fields(post)
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            for key in ['id', 'action', 'civil_status',
                        'nationality_country_id', 'educational_attainment',
                        'dob', 'house_type']:
                if not values.get(key) and key in values:
                    values.pop(key)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'country_id': int(values.pop('country_id', 0))})
                values.update({'zip': values.pop('zipcode', '')})
                barangay = self.get_barangay(post.get('zipcode'))
                if post.get('dob'):
                    age = date.today().year - datetime.strptime(post.get('dob'), "%Y-%m-%d").year
                    age_range = request.env['res.partner.age.range'].search([('range_from', '<=', age), ('range_to', '>=', age)], limit=1)
                    self.age_range_id = age_range[:1] and age_range.id or False
                if post.get('street2'):
                    values.update({'street': post.get('street2'),
                                   'street2': post.get('street')})
                values.update({
                    'lastname': post.get('lastname'),
                    'middle_name': post.get('middle_name'),
                    'firstname': post.get('firstname'),
                    'suffix_name': post.get('suffix_name'),
                    'barangay_id': barangay.id,
                    'city_id': barangay.city_id.id,
                    'city': f"{barangay.name}, {barangay.city_id.name}",
                    'province_id': barangay.province_id.id,
                    'state_id': barangay.state_id.id,
                    'island_group_id': barangay.island_group_id.id,
                    'continent_region_id': barangay.continent_region_id.id,
                    'continent_id': barangay.continent_id.id,
                    'marital': values.pop('civil_status', ''),
                    'educational_attaiment_id': values.pop('educational_attainment'),
                    'date_of_birth': values.pop('dob', ''),
                    'number_of_dependencies': values.pop('dependents', 0),
                    'house_type_id': values.pop('house_type', 0),
                    'employment_status_id': values.pop('employment_status', 0),
                    'age_range_id':  age_range[:1] and age_range.id or False,
                    'age': age,
                })
                if not values.get('house_type_id'):
                    values.pop('house_type_id')

                if not values.get('employment_status_id'):
                    values.pop('employment_status_id', 0)
                if values.get('state_id') == '':
                    values.update({'state_id': False})
                if not values.get('emp_country_id'):
                    values.pop('emp_country_id')
                if not values.get('emp_industry_id'):
                    values.pop('emp_industry_id')
                if not values.get('employment_date'):
                    values.pop('employment_date')
                values.update({
                    'emp_zip': values.pop('emp_zipcode'),
                    'salary_income': values.get('salary_income') and locale.atof(values.pop('salary_income')) or 0,
                    'other_income': values.get('other_income') and locale.atof(values.pop('other_income')) or 0,
                })
                if post.get('emp_company_name') and values.get('emp_zipcode') and values.get('emp_country_id') == 176:
                    emp_barangay = self.get_barangay(values.get('emp_zipcode'))
                    values.update({
                        'emp_barangay_id': emp_barangay.id,
                        'emp_city_id': emp_barangay.city_id.id,
                        'emp_city': f"{emp_barangay.name}, {emp_barangay.city_id.name}",
                        'emp_region':f"{emp_barangay.province_id.name}, {emp_barangay.state_id.name}",
                        'emp_province_id': emp_barangay.province_id.id,
                        'emp_state_id': emp_barangay.state_id.id,
                        'emp_island_group_id': emp_barangay.island_group_id.id,
                        'emp_continent_region_id': emp_barangay.continent_region_id.id,
                        'emp_continent_id': emp_barangay.continent_id.id,
                    })
                business_data = [
                        values.pop('business_name'),values.pop('business_industry'),
                        values.pop('business_type'), values.pop('establishment_date'),
                        values.pop('business_country_id'), values.pop('business_zipcode'), values.pop('business_city'),
                        values.pop('business_region'), values.pop('business_street'), values.pop('business_street2')
                    ]
                loan_data = [
                    [
                        values.pop(f'loan_id{count}'),
                        values.pop(f'loan_institution{count}'),
                        values.pop(f'loan_type{count}'),
                        values.pop(f'loan_granted{count}'),
                        values.pop(f'loan_maturity{count}'),
                        values.pop(f'loan_amortization{count}')
                    ] for count in range(1, 5)
                ]
                credit_card_data = [
                    [
                        values.pop(f'credit_card_id{count}'),
                        values.pop(f'credit_card_name{count}'),
                        values.pop(f'credit_card_holder{count}')
                    ] for count in range(1, 5)
                ]
                contact_reference_data = [
                    [
                        values.pop(f'contact_reference_id{count}'),
                        values.pop(f'contact_reference_name{count}'),
                        values.pop(f'contact_reference_relationship{count}'),
                        values.pop(f'contact_reference_address{count}'),
                        values.pop(f'contact_reference_contact_number{count}'),
                        values.pop(f'contact_reference_other{count}')
                    ] for count in range(1, 5)
                ]
                if not action or not action in ['create_spuase', 'create_co-borrower', 'create_attorney-in-fact']:
                    partner.sudo().write(values)
                    user_partner = request.env.user.partner_id.sudo()
                    if action == 'edit_co-borrower':
                        user_partner.write({'co_borrower_relationship_id': buyer_relationship})
                    elif action == 'edit_attorney-in-fact':
                        user_partner.write({'attorney_borrower_relationship_id': buyer_relationship})
                else:
                    partner = request.env['res.partner'].sudo().create(values)
                    if action == 'create_spuase':
                        request.env.user.partner_id.sudo().write({'spouse_partner_id': partner.id})
                    elif action == 'create_co-borrower':
                        request.env.user.partner_id.sudo().write({'co_borrower_partner_id': partner.id, 'co_borrower_relationship_id': buyer_relationship})
                    elif action == 'create_attorney-in-fact':
                        request.env.user.partner_id.sudo().write({'attorney_partner_id': partner.id, 'attorney_borrower_relationship_id': buyer_relationship})
                if partner[:1]:
                    business = request.env['res.partner.business'].sudo().search([('partner_id', '=', partner.id)], limit=1)

                    self.process_business_data(partner, business, business_data)
                    for loan in loan_data:
                        self.process_loan(partner, loan)
                    for card in credit_card_data:
                        self.process_credit_card(partner, card)
                    for contact_reference_rec in contact_reference_data:
                        self.process_contact_reference(partner, contact_reference_rec)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        province = request.env['res.country.province'].sudo().search([])
        city = request.env['res.country.city'].sudo().search([])
        # barangay = request.env['res.barangay'].sudo().search([])
        educational_attaiment = request.env['res.partner.educational.attainment'].sudo().search([])
        buyer_relationship = request.env['res.partner.buyer.relationship'].sudo().search([])
        employment_status = request.env['res.partner.employment.status'].sudo().search([])
        industry = request.env['res.partner.industry'].sudo().search([])
        property_purpose = request.env['res.partner.property.purpose'].sudo().search([])
        house_type = request.env['res.partner.house.type'].sudo().search([])
        business, loan_rec, credit_card_rec, contact_reference_rec = [[] for count in range(4)]
        if partner:
            business = request.env['res.partner.business'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            loan_rec = request.env['res.partner.loan'].sudo().search([('partner_id', '=', partner.id)], order="id desc")
            credit_card_rec = request.env['res.partner.credit.card.issuer'].search([('partner_id', '=', partner.id)], order="id desc")
            contact_reference_rec = request.env['res.partner.personal.references'].search([('partner_id', '=', partner.id)], order="id desc")

        loan = loan_rec[:1] and [[rec.id, rec.name, rec.type_of_loan, rec.date_paid, rec.maturity_date, rec.monthly_amortization] for rec in loan_rec] or []
        credit_card = credit_card_rec[:1] and [[rec.id, rec.name, rec.card_holder_name] for rec in credit_card_rec] or []
        contact_reference = contact_reference_rec[:1] and [[rec.id, rec.name, rec.buyer_relationship_id, rec.address, rec.contact_number, rec.other] for rec in contact_reference_rec] or []

        values.update({
            'id': id,
            'current_relationship': current_relationship,
            'company_type': company_type,
            'action': action,
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
            'province': province,
            'city': city,
            # 'barangay': barangay,
            'educational_attainment': educational_attaiment,
            'buyer_relationship': buyer_relationship,
            'employment_status': employment_status,
            'industry': industry,
            'property_purpose': property_purpose,
            'house_type': house_type,
            'business': business,
            'loan': loan,
            'credit_card': credit_card,
            'contact_reference': contact_reference,
            'business_type': [
                            ('proprietor', 'Single Proprietorship'),
                            ('partnership', 'Partnership'),
                            ('corporation', 'Corporation'),
                            ('cooperative', 'Cooperative')
                        ],
            'gender': [('male', 'Male'),
                        ('female', 'Female'),
                        ('other', 'Other')],
            'marital': [
                            ('single', 'Single'),
                            ('married', 'Married'),
                            ('cohabitant', 'Legal Cohabitant'),
                            ('widower', 'Widower'),
                            ('divorced', 'Divorced'),
                            ('separated', 'Separated'),
                            ('annulled', 'Annulled')
                        ],
            'contract_status': [
                                    ('regular', 'Regular'),
                                    ('contractual', 'Constractual'),
                                    ('project_based', 'Project Based')
                                ],
            'position_level': [
                                ('rank_file', 'Rank and File/Staff/Clerk'),
                                ('supervisor', 'Supervisor/Team Lead'),
                                ('manager', 'Manager/Director'),
                                ('executive', 'Executive Officer'),
                                ('professional', 'Professional (Doctor/Lawyer/Engineer/Architect)')
                            ]

        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
