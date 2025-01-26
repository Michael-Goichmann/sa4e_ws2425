package com.example;
import org.apache.camel.builder.RouteBuilder;
import java.io.File;
import java.util.HashMap;
import java.util.Map;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;
import org.apache.camel.Exchange;
import org.apache.camel.Processor;

public class XmasOcrRoute extends RouteBuilder {
    @Override
    public void configure() throws Exception {
        // Enable idempotent processing using a file-based repository
        from("file:scanned_letters?noop=true&idempotent=true&idempotentRepository=#fileStore")
            .routeId("ocrLettersRoute")
            .process(exchange -> {
                String filePath = exchange.getIn().getHeader("CamelFilePath", String.class);
                System.out.println("DEBUG => Processing file: " + filePath);
                File inputFile = new File(filePath);
                if (!inputFile.exists()) {
                    throw new RuntimeException("File not found for OCR: " + filePath);
                }
                
                // Initialize Tesseract with explicit data path
                Tesseract tesseract = new Tesseract();
                tesseract.setDatapath("C:/Program Files/Tesseract-OCR/tessdata");
                tesseract.setLanguage("eng");
                
                // Perform OCR
                String ocrText = tesseract.doOCR(inputFile);
                System.out.println("DEBUG => Raw OCR text: " + ocrText);
                
                // Parse the OCR text to extract name and wish
                String name = "Unknown";
                String wish = "Unknown";
                
                // Split text into lines and process each line
                for (String line : ocrText.split("\n")) {
                    line = line.trim();
                    if (line.toLowerCase().startsWith("name:")) {
                        name = line.substring(5).trim();
                    } else if (line.toLowerCase().startsWith("wish:")) {
                        wish = line.substring(5).trim();
                        // Collect any additional lines as part of the wish
                        StringBuilder wishBuilder = new StringBuilder(wish);
                        boolean isMultilineWish = false;
                        for (String remainingLine : ocrText.split("\n")) {
                            if (isMultilineWish && !remainingLine.toLowerCase().startsWith("name:")) {
                                wishBuilder.append(" ").append(remainingLine.trim());
                            }
                            if (remainingLine.trim().equals(wish)) {
                                isMultilineWish = true;
                            }
                        }
                        wish = wishBuilder.toString().trim();
                    }
                }
                
                System.out.println("DEBUG => Extracted name: " + name);
                System.out.println("DEBUG => Extracted wish: " + wish);
                
                Map<String, Object> body = new HashMap<>();
                body.put("name", name);
                body.put("wish", wish);
                body.put("status", 1);
                exchange.getIn().setBody(body);
                
                // Store the name in a header for logging
                exchange.getIn().setHeader("ExtractedName", name);
            })
            .marshal().json()
            .to("http://192.168.56.10:5003/wishes?httpMethod=POST")
            .log("Processed and uploaded letter for ${header.ExtractedName} -> XmasWishes: ${header.CamelFileName}");
    }
}