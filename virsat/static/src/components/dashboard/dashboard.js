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
        this.action.doAction("virsat.action_vr_game_result_report")
    }

    openPerGameReport() {
        this.action.doAction("virsat.action_vr_game_sessions_per_game")
    }

    openPerSessionReport() {
        this.action.doAction("virsat.action_vr_game_sessions_per_trainee")
    }
}

VirsatDashboard.components = { Layout, PieChart };
VirsatDashboard.template = "virsat.dashboard";

registry.category("actions").add("virsat.dashboard", VirsatDashboard);