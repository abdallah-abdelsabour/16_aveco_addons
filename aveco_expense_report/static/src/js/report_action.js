/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";


function avecoExpenseReportDownload(env, action) {
    const wizardId = action.context.wizard_id;

    if (!wizardId) {
        env.services.notification.add(
            "Missing wizard ID for report generation",
            { type: "danger" }
        );
        return;
    }

    const formData = new FormData();
    formData.append("wizard_id", wizardId);

    download({
        url: "/aveco_expense_report/download_xlsx",
        data: {
            wizard_id: wizardId,
        },
    });

    if (action.context && action.context.dialog_size) {
        return { type: "ir.actions.act_window_close" };
    }
}

registry.category("actions").add("aveco_expense_report_download", avecoExpenseReportDownload);
