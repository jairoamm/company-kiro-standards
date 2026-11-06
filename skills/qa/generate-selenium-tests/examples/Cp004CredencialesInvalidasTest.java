package demo.e2e;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

/** Ejemplo sintético de CP-004. No se ejecuta como parte de la Skill. */
class Cp004CredencialesInvalidasTest {
    private static final Path FAILURE_SCREENSHOT = Path.of(
        "build/evidence/e2e/HU-DEMO-001/CP-004/failure.png"
    );

    private final By email = By.id("login-email");
    private final By credential = By.id("login-credential");
    private final By submit = By.cssSelector("[data-testid='login-submit']");
    private final By alert = By.cssSelector("[role='alert']");

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeEach
    void setUp() {
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @AfterEach
    void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    void shouldShowInvalidCredentialsMessageWhenCp004UsesInvalidUser() throws IOException {
        try {
            driver.get(requireBaseUrl());
            wait.until(ExpectedConditions.visibilityOfElementLocated(email))
                .sendKeys("qa.invalid@example.test");
            wait.until(ExpectedConditions.visibilityOfElementLocated(credential))
                .sendKeys("synthetic-invalid-value");
            wait.until(ExpectedConditions.elementToBeClickable(submit)).click();

            WebElement message = wait.until(
                ExpectedConditions.visibilityOfElementLocated(alert)
            );
            assertEquals("Credenciales inválidas", message.getAccessibleName());
        } catch (AssertionError | RuntimeException error) {
            captureFailureScreenshot();
            throw error;
        }
    }

    private String requireBaseUrl() {
        String baseUrl = System.getenv("BASE_URL");
        if (baseUrl == null || baseUrl.isBlank()) {
            throw new IllegalStateException("BASE_URL debe identificar el destino autorizado");
        }
        return baseUrl;
    }

    private void captureFailureScreenshot() throws IOException {
        Files.createDirectories(FAILURE_SCREENSHOT.getParent());
        byte[] image = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
        Files.write(FAILURE_SCREENSHOT, image);
    }
}
