import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class AppTest {
    @Test
    void greet_returnsGreeting() {
        assertEquals("Hello, world!", App.greet("world"));
    }
}
