package com.example;
import org.apache.camel.CamelContext;
import org.apache.camel.impl.DefaultCamelContext;
import org.apache.camel.support.processor.idempotent.FileIdempotentRepository;
import org.apache.camel.spi.IdempotentRepository;
import java.io.File;

public class XmasCamelApp {
    public static void main(String[] args) throws Exception {
        CamelContext context = new DefaultCamelContext();
        
        // Configure file-based idempotent repository using the correct type
        IdempotentRepository fileStore = FileIdempotentRepository.fileIdempotentRepository(
            new File("C:/Users/mgoic/Pictures/scanned_letters/.camel-idempotent"));
        
        // Register the repository
        context.getRegistry().bind("fileStore", fileStore);
        
        // Add routes
        context.addRoutes(new XmasOcrRoute());
        
        // Start the context
        context.start();
        System.out.println("Camel OCR-Route is running... press Ctrl+C to stop.");
        
        // Keep the application running
        while (true) {
            Thread.sleep(10000);
        }
    }
}