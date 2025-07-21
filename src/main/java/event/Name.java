package event;

import com.sedmelluq.discord.lavaplayer.player.AudioLoadResultHandler;
import com.sedmelluq.discord.lavaplayer.player.AudioPlayerManager;
import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager;
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers;
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException;
import com.sedmelluq.discord.lavaplayer.track.*;
import com.sedmelluq.discord.lavaplayer.track.AudioPlaylist;
import com.sedmelluq.discord.lavaplayer.track.AudioTrack;
import net.dv8tion.jda.api.MessageBuilder;
import net.dv8tion.jda.api.audio.AudioSendHandler;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.events.message.guild.GuildMessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.io.File;
import java.nio.ByteBuffer;
import java.util.Random;

public class Name extends ListenerAdapter {
    boolean isGo = true;
    final String ABSPATH = "YOUR PATH"; //You may need to change this
    //rivate final AudioPlayerManager playerManager = new DefaultAudioPlayerManager();

    /*public Name() {
        AudioSourceManagers.registerRemoteSources(playerManager);
        AudioSourceManagers.registerLocalSource(playerManager);
    }*/
    @Override
    public void onGuildMessageReceived(@NotNull GuildMessageReceivedEvent event) {
        String message = event.getMessage().getContentRaw();
        if (event.getAuthor().isBot() || event.isWebhookMessage()) {
            return;
        }
        if (message.contains("/stop go")) {
            isGo = false;
        }
        if (message.contains("/start go")) {
            isGo = true;
        }
        if (message.contains("一輩子") || message.contains("一世")) {
            //random two images
            Random rand = new Random();
            int n = rand.nextInt(2);
            switch (n) {
                case 0:
                    //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/畢竟這是一輩子的事.jpg").queue();
                    event.getChannel().sendFile(getFile("img\\畢竟這是一輩子的事.jpg"), "畢竟這是一輩子的事.jpg").queue();
                    break;
                case 1:
                    //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/%E6%98%AF%E4%B8%80%E8%BC%A9%E5%AD%90%E5%96%94_%E4%B8%80%E8%BC%A9%E5%AD%90.jpg").queue();
                    event.getChannel().sendFile(getFile("img\\是一輩子喔_一輩子.jpg"), "是一輩子喔_一輩子.jpg").queue();
                    break;
                default:
                    break;
            }
            return;
        }
        if (message.contains("No") || message.contains("no") || message.contains("不行") || message.contains("不能") || message.contains("不可以") || message.contains("不要") || message.contains("不想") || message.contains("dame") || message.contains("だめ")) {
            Random rand = new Random();
            int n = rand.nextInt(2);
            switch (n) {
                case 0:
                    //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/不行.jpg").queue();
                    event.getChannel().sendFile(getFile("img\\不行.jpg"), "不行.jpg").queue();
                    break;
                case 1:
                    //event.getChannel().sendMessage("https://ave-mujica-images.pages.dev/assets/%E4%B8%8D%E5%8F%AF%E4%BB%A5-BiaRmwz4.webp").queue();
                    event.getChannel().sendFile(getFile("img\\不可以-BiaRmwz4.webp"), "不可以-BiaRmwz4.webp").queue();
                    break;
                default:
                    break;
            }
            return;
        }
        if (message.contains("春日影")) {
            //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/為什麼要演奏春日影.jpg").queue();
            event.getChannel().sendFile(getFile("img\\為什麼要演奏春日影.jpg"), "為什麼要演奏春日影.jpg").queue();
            //join the voice channel
            //event.getGuild().getAudioManager().openAudioConnection(event.getMember().getVoiceState().getChannel()); //kinda buggy

            /*playerManager.loadItem("C:\\Users\\kinglingmk1\\Desktop\\Lab02\\DiscordBot\\src\\main\\java\\mp3\\春日影.mp3", new AudioLoadResultHandler() {
                @Override
                public void trackLoaded(AudioTrack track) {
                    event.getGuild().getAudioManager().setSendingHandler(new AudioSendHandler() {
                        @Override
                        public boolean canProvide() {
                            return false;
                        }

                        @Override
                        public @Nullable ByteBuffer provide20MsAudio() {
                            return null;
                        }
                    });
                    playerManager.createPlayer().playTrack(track);
                }

                @Override
                public void playlistLoaded(AudioPlaylist playlist) {
                    // Handle playlist if needed
                }

                @Override
                public void noMatches() {
                    // Notify user that no matches were found
                }

                @Override
                public void loadFailed(FriendlyException e) {

                }
            }); */
            return;
        }
        if (message.contains("go") || message.contains("Go") || message.contains("GO") || message.contains("gO")) {
            if (isGo) {
                event.getChannel().sendMessage("還在Go 還在Go").queue();
                //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/我也一樣.jpg?t=1739679323762").queue();
                event.getChannel().sendFile(getFile("img\\我也一樣.jpg"), "我也一樣.jpg").queue();
                return;
            }
            return;
        }
        if (message.contains("Me too") || message.contains("me too") || message.contains("我也是") || message.contains("我也是啊") || message.contains("我也一樣") || message.contains("我也是呀")) {
            //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/我也一樣.jpg?t=1739679323762").queue();
            event.getChannel().sendFile(getFile("img\\我也一樣.jpg"), "我也一樣.jpg").queue();
            return;
        }
        if (message.contains("Mujica") || message.contains("mujica") || message.contains("ムヒカ") || message.contains("穆希卡") || message.contains("ミュヒカ")) {
            //event.getChannel().sendMessage("https://drive.miyago9267.com/d/file/img/mygo/現在正是復權的時刻.jpg?t=1739680908017").queue();
            event.getChannel().sendFile(getFile("img\\現在正是復權的時刻.jpg"), "現在正是復權的時刻.jpg").queue();
            return;
        }
        if(message.equals("!deepseek_mode")){
            event.getChannel().sendMessage("思").queue(sentMessage -> {
                sleep(20);
                sentMessage.editMessage("思考").queue(sentsMessage -> {
                    sleep(20);
                    sentsMessage.editMessage("思考中").queue(sentssMessage -> {
                        sleep(20);
                        sentssMessage.editMessage("思考中.").queue(sentsssMessage -> {
                            sleep(20);
                            sentsssMessage.editMessage("思考中..").queue(sentssssMessage -> {
                                sleep(20);
                                sentssssMessage.editMessage("思考中...").queue();
                            });
                        });
                    });
                });
            });
            sleep(5000);
            event.getChannel().sendMessage("服务器繁忙，请稍后再试").queue();
            return;
        }
        //if tagged the bot
        if (event.getMessage().getMentionedUsers().contains(event.getJDA().getSelfUser()) || message.contains("Soyo") || message.contains("soyo") || message.contains("そよ") || message.contains("長崎そよ") || message.contains("長崎爽世") || message.contains("そよちゃん") || message.contains("爽世") || message.contains("素世") || message.contains("長崎素世")){
            //event.getChannel().sendMessage("https://ave-mujica-images.pages.dev/assets/%E5%B9%B9%E5%98%9B-CStDUUrz.webp").queue();
            event.getChannel().sendFile(getFile("img\\幹嘛-CStDUUrz.webp"), "幹嘛-CStDUUrz.webp").queue();
            return;
        }
    }
    private void sleep(int i) {
        try {
            Thread.sleep(i);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
    private File getFile(String filename){
        return new File(ABSPATH + filename);
    }
}
