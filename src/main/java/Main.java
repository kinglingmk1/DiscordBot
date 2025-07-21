import event.Name;
import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.requests.GatewayIntent;
import javax.security.auth.login.LoginException;

public class Main {
    public static void main(String[] args) throws LoginException, InterruptedException {
        JDA jda = JDABuilder.createDefault(getTOKEN()).build();
        jda.addEventListener(new Name());
        jda.addEventListener(new command.Setting());
        jda.awaitReady();
    }
    private static String getTOKEN(){
        return "TOKEN"; //Finish call me add
    }
}
