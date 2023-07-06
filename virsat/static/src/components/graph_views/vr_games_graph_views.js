/** @odoo-module */

import { registry } from "@web/core/registry"
import { graphView } from "@web/views/graph/graph_view"
import { GraphRenderer } from "@web/views/graph/graph_renderer"
import { getColor, getBorderWhite } from "@web/views/graph/colors";
import { _lt } from "@web/core/l10n/translation";

const NO_DATA = _lt("No data");

class VrGameSessionsGraphRenderer extends GraphRenderer {
    getBarChartData() {
        const { domains, stacked } = this.model.metaData;
        const data = this.model.data;
        for (let index = 0; index < data.datasets.length; ++index) {
            const dataset = data.datasets[index];
            // used when stacked
            if (stacked) {
                dataset.stack = domains[dataset.originIndex].description || "";
            }
            // set dataset color
            if (dataset.label.includes("Failed") || dataset.label.includes("Passed")){
                dataset.backgroundColor = this.getPassFailedColor(dataset.label);
            }else {
                dataset.backgroundColor = getColor(index, this.cookies.current.color_scheme);
            }
        }

        return data;
    }

    getPassFailedColor(status){
        const passed_color = "green"
        const failed_color = "red"

        return status == "Passed" ? passed_color : failed_color;
    }


}

export const vrGameSessionsGraphView = {
    ...graphView,
    Renderer: VrGameSessionsGraphRenderer,
}

registry.category("views").add("vr_game_sessions_graph_view", vrGameSessionsGraphView)