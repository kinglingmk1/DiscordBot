// File: src/main/java/command/Setting.java
package command;

import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;

public class Setting extends ListenerAdapter {
    @Override
    public void onMessageReceived(MessageReceivedEvent event) {
        String message = event.getMessage().getContentRaw();

        if (message.startsWith("!help")) {
            event.getAuthor().openPrivateChannel().flatMap(channel -> channel.sendMessage("!help for help")).queue();
        }
        // Add more commands here
    }
}