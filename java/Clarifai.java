package test;

import java.io.*;
import java.net.*;
import javax.net.ssl.*;

public class Clarifai {
	public static void main(String[] args) {
		
		String concept = "coca cola can";
		String accessToken = "P7cEzNBa9vTylhJOcFaOd8u8ejDC0L";
		String guess = "http://i.imgur.com/Y93pcRD.png";
		
		try {
			URL url = new URL("https://api-alpha.clarifai.com/v1/curator/concepts/default/" + URLEncoder.encode(concept, "UTF-8") + "/predict");
		    HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();
		    
	        String data = URLEncoder.encode("urls", "UTF-8") + "=" + URLEncoder.encode(guess, "UTF-8");
		
		    conn.setDoOutput(true);
		    conn.setDoInput(true);
		    conn.setRequestMethod("POST");
		    conn.setRequestProperty("Authorization", "Bearer " + accessToken);
		    conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
		
		    conn.connect();
		    
		    StringBuilder stb = new StringBuilder();
		    OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
		    wr.write(data);
		    wr.flush();
		    
		    System.out.println(data);
		
		    // Get the response
		    BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
		    
		    System.out.println("got connection");
		    
		    String line;
		    while ((line = rd.readLine()) != null) {
		        stb.append(line).append("\n");
		        System.out.println(stb.toString());
		    }
		    wr.close();
		    rd.close();
		
		    System.out.println(stb.toString());
			
			
		} catch(Exception e) {
			e.printStackTrace();
		}
		
	}
}
