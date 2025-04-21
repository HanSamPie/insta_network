import java.awt.Color;

public class CommunityColor {
    private static final Color[] PALETTE = {
        Color.decode("#1f78b4"), Color.decode("#33a02c"), Color.decode("#e31a1c"),
        Color.decode("#ff7f00"), Color.decode("#6a3d9a"), Color.decode("#b15928")
    };

    public static Color getColor(int communityId) {
        return PALETTE[communityId % PALETTE.length];
    }
}
