# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Mashood K.U (Contact : odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
{
    'name': 'Recurring Payments in Accounts',
    'version': '13.0.1.1.1',
    'summary': """An advanced way to handle your repeating payments easily.
                It helps to handle those type of payments by generating journal entries
                 automatically based on your conditions. """,
    'description': """An advanced way to handle your repeating payments easily.""",
    'category': 'Accounting',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base', 'account'],
    'website': 'https://www.cybrosys.com',
    'data': [
        'views/recurring_payments_view.xml',
        'wizard/wizard_view.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 29.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
