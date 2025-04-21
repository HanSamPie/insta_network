import org.gephi.graph.api.*;
import org.gephi.io.importer.api.*;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2Builder;
import org.gephi.project.api.*;
import org.gephi.statistics.plugin.Modularity;
import org.openide.util.Lookup;

import java.io.File;

public class GephiScript {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java GephiScript <input.graphml> <output.graphml>");
            System.exit(1);
        }

        String inputFilePath = args[0];
        String outputFilePath = args[1];

        // Create a new project and workspace in Gephi
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        // Import GraphML file
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        Container container;
        try {
            File file = new File(inputFilePath);
            container = importController.importFile(file);
            container.getLoader().setEdgeDefault(EdgeDirectionDefault.DIRECTED);   // or UNDIRECTED
        } catch (Exception ex) {
            ex.printStackTrace();
            return;
        }
        importController.process(container, new DefaultProcessor(), workspace);

        // Retrieve graph and run layout
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();
        Graph graph = graphModel.getGraph();

        // Layout: ForceAtlas2
        ForceAtlas2 layout = new ForceAtlas2Builder().buildLayout();
        layout.setGraphModel(graphModel);
        layout.initAlgo();
        layout.setAdjustSizes(true);
        layout.setScalingRatio(10.0);
        layout.setGravity(1.0);

        // Run layout for 1000 iterations
        for (int i = 0; i < 1000 && layout.canAlgo(); i++) {
            layout.goAlgo();
        }
        layout.endAlgo();

        // Modularity for community detection
        Modularity modularity = new Modularity();
        modularity.execute(graphModel);
        Column modularityCol = graphModel.getNodeTable().getColumn(Modularity.MODULARITY_CLASS);

        // Set node size and color based on attributes
        for (Node node : graph.getNodes()) {
            // Label by username
            Object username = node.getAttribute("username");
            if (username != null) {
                node.setLabel(username.toString());
            }

            // Node size by followers_count
            Object followers = node.getAttribute("followers_count");
            if (followers instanceof Number) {
                float size = ((Number) followers).floatValue();
                node.setSize(size / 50f);  // Adjust the scale as needed
            }

            // Color nodes based on community (modularity class)
            Object modClass = node.getAttribute(modularityCol);
            if (modClass instanceof Integer) {
                int community = (Integer) modClass;
                node.setColor(CommunityColor.getColor(community));
            }

            // Adjust alpha (color brightness) based on in-degree
            float inWeight = graph.getInDegree(node, true);  // Weighted in-degree
            float brightness = Math.min(1f, inWeight / 50f);  // Adjust brightness
            node.setAlpha(brightness);
        }

        // Export the modified graph to GraphML
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        try {
            ec.exportFile(new File(outputFilePath));
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }
}
