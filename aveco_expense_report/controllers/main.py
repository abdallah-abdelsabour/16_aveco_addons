from odoo import http
from odoo.http import request, content_disposition
import json


class ExpenseReportController(http.Controller):

    @http.route('/aveco_expense_report/download_xlsx', type='http', auth='user', methods=['POST'], csrf=False)
    def download_xlsx_report(self, wizard_id, **kw):
        wizard_id = int(wizard_id)
        wizard = request.env['expense.report.wizard'].browse(wizard_id)

        if not wizard.exists():
            return request.not_found()

        try:
            data = wizard._get_report_data()
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )

        file_data = wizard.generate_xlsx_report(data)

        filename = 'Expense_Report_%s_to_%s.xlsx' % (
            wizard.date_from.strftime('%Y%m%d'),
            wizard.date_to.strftime('%Y%m%d')
        )

        response = request.make_response(
            file_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename)),
                ('Content-Length', len(file_data))
            ]
        )

        response.set_cookie('fileToken', 'dummy-token')

        return response
