/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { Domain } from "@web/core/domain";
import { session } from "@web/session";
import { PieChart } from "../pie_chart/pie_chart";

const { Component, useSubEnv, onWillStart } = owl;

class VirsatDashboard extends Component {
    setup(){
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.display = {
            controlPanel: { "top-right": false, "bottom-right": false },
        };

        this.action = useService("action");
        this.rpc = useService("rpc");

        onWillStart(async () => {
            this.statistics = await this.rpc("/virsat/statistics");
            this.companies = await this.rpc("/virsat/selected-companies");
        });
    }

     openGameResultsReport() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Game Results",
            res_model: "vr.game.result.report",
            views: [[false, "kanban"], [false, "tree"]],
            domain: [['company_id', 'in', this.companies]]
        });
    }
}

VirsatDashboard.components = { Layout, PieChart };
VirsatDashboard.template = "virsat.dashboard";

registry.category("actions").add("virsat.dashboard", VirsatDashboard);