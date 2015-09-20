package com.example.jadesym.hackmit;

import android.app.Dialog;
import android.app.ListActivity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Outline;
import android.graphics.drawable.Drawable;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.StrictMode;
import android.support.design.widget.FloatingActionButton;
import android.util.Base64;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewOutlineProvider;
import android.view.Window;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.GridView;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.HashMap;

import org.json.*;


import javax.net.ssl.HttpsURLConnection;

public class MainActivity extends ListActivity {


    private static final int CAMERA_REQUEST = 1888;
    private static final String API_KEY = "06a498489dc5bf7";
    private ListView list;
    private ArrayList<String> strList = new ArrayList<>();
    private ArrayList<Drawable> drawList = new ArrayList<>();
    private CustomListAdapter adapter;
    private FloatingActionButton fab;
    private FloatingActionButton fab_done;
    private HashMap<String, String> urlToConcept = new HashMap<>();
    private GPSTracker gpsTracker;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        super.onCreate(savedInstanceState);

        gpsTracker = new GPSTracker(this);
        setContentView(R.layout.activity_main);
        fab = (FloatingActionButton) this.findViewById(R.id.fab);
        fab_done = (FloatingActionButton) this.findViewById(R.id.fab_done);


        adapter=new CustomListAdapter(this, strList, drawList);
        list= getListView();
        list.setAdapter(adapter);
        View header = getLayoutInflater().inflate(R.layout.header, null);
        list.addFooterView(header);

        list.setOnItemClickListener(new AdapterView.OnItemClickListener() {

            @Override
            public void onItemClick(AdapterView<?> parent, View view,
                                    int position, long id) {
                // TODO Auto-generated method stub
                String Slecteditem = strList.get(+position);
                Toast.makeText(getApplicationContext(), Slecteditem, Toast.LENGTH_SHORT).show();

            }
        });

        ViewOutlineProvider viewOutlineProvider = new ViewOutlineProvider() {
            @Override
            public void getOutline(View view, Outline outline) {
                // Or read size directly from the view's width/height
                int size = getResources().getDimensionPixelSize(R.dimen.fab_size);
                outline.setOval(0, 0, size, size);
            }
        };


        fab.setOutlineProvider(viewOutlineProvider);
        if (android.os.Build.VERSION.SDK_INT > 9) {
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);
        }

        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startCamera(view);
            }
        });

        fab_done.setOutlineProvider(viewOutlineProvider);
        fab_done.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (urlToConcept.size() < 1) {
                    Toast.makeText(getApplicationContext(), "You need at least one item to call for a delivery!", Toast.LENGTH_SHORT).show();
                } else {

                    String[] splited = getGPS().split(" ");
                    String latitude = splited[0];
                    String longitude = splited[1];
                    sendToShelter(latitude, longitude);

                }
            }
        });

    }

    public String getGPS() {
        String latLong = "";
        if (gpsTracker.getIsGPSTrackingEnabled()) {
            String stringLatitude = String.valueOf(gpsTracker.latitude);

            String stringLongitude = String.valueOf(gpsTracker.longitude);
            latLong = stringLatitude + " " + stringLongitude;
            Toast.makeText(getApplicationContext(), latLong, Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(getApplicationContext(), "Could not get gps location!", Toast.LENGTH_SHORT).show();
            return null;
        }
        return latLong;

    }



    public void sendToShelter(String latitude, String longitude) {

        JSONObject jsonPayload = new JSONObject(urlToConcept);

        try {
            jsonPayload.put("lat", Double.parseDouble(latitude));
            jsonPayload.put("lng", Double.parseDouble(longitude));
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Non-double latitude or longitude!", Toast.LENGTH_SHORT);
        }
        boolean clear = true;
        try {
            createDelivery(jsonPayload);
        } catch (Exception e) {
            System.out.println("Could not successfully send the delivery!");
            clear = false;
        }
        if (clear) {
            urlToConcept.clear();
            strList.clear();
            drawList.clear();
            adapter.notifyDataSetChanged();
            Toast.makeText(getApplicationContext(), "Delivery successfully arranged! Postmates Driver will be arriving near you soon!", Toast.LENGTH_SHORT).show();
        }

    }

    public void startCamera(View v) {
        Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(cameraIntent, CAMERA_REQUEST);
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        if (requestCode == CAMERA_REQUEST && resultCode == RESULT_OK) {
            Bitmap photo = (Bitmap) data.getExtras().get("data");
//            imageView.setImageBitmap(photo);
            uploadPhoto(photo);
        } else {
            Toast.makeText(getApplicationContext(), "Camera Error!", Toast.LENGTH_SHORT).show();
        }
    }

    public static Drawable LoadImageFromWebOperations(String url) {
        try {
            InputStream is = (InputStream) new URL(url).getContent();
            Drawable d = Drawable.createFromStream(is, "src name");
            return d;
        } catch (Exception e) {
            return null;
        }
    }

    public static void createDelivery(JSONObject jsonPayload) throws Exception {

        StringBuilder sb = new StringBuilder();
        URL url;
        HttpURLConnection urlConn;

        url = new URL("http://hackmit.joshcai.com/create_delivery");
        urlConn = (HttpURLConnection) url.openConnection();
        urlConn.setDoInput(true);
        urlConn.setDoOutput(true);
        urlConn.setRequestMethod("POST");

//        urlConn.setUseCaches(false);
        urlConn.connect();
        String jsonStr = jsonPayload.toString();
        System.out.println(jsonStr);
        OutputStreamWriter wr = new OutputStreamWriter(urlConn.getOutputStream());

        wr.write(jsonStr);
        wr.flush();
        wr.close();

        // Get the response
        BufferedReader rd = new BufferedReader(new InputStreamReader(urlConn.getInputStream()));
        String line;
        while ((line = rd.readLine()) != null) {
            sb.append(line).append("\n");
        }
        wr.close();
        rd.close();

        System.out.println(sb);

    }

    public static String getImgurContent(Bitmap bitmap) throws Exception {
        URL url = new URL("https://api.imgur.com/3/upload");
        HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();


        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        System.out.println("Writing image...");
        bitmap.compress(Bitmap.CompressFormat.PNG, 100 /*ignored for PNG*/, baos);

//        String data = URLEncoder.encode("image", "UTF-8") + "=" + URLEncoder.encode(Base64.encodeToS4tring(baos.toByteArray()), "UTF-8");
        String data = URLEncoder.encode("image", "UTF-8") + "=" + URLEncoder.encode(Base64.encodeToString(baos.toByteArray(), Base64.DEFAULT), "UTF-8");
        System.out.println(data);

        conn.setDoOutput(true);
        conn.setDoInput(true);
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Authorization", "Client-ID " + API_KEY);
        conn.setRequestProperty("Content-Type",
                "application/x-www-form-urlencoded");

        conn.connect();
        StringBuilder stb = new StringBuilder();
        OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
        wr.write(data);
        wr.flush();

        // Get the response
        BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String line;
        while ((line = rd.readLine()) != null) {
            stb.append(line).append("\n");
        }
        wr.close();
        rd.close();

        return stb.toString();
    }


    private void uploadPhoto(Bitmap image) {
        try {
            String outJson = getImgurContent(image);
            JSONObject obj = (JSONObject) new JSONObject(outJson).get("data");
            String url = obj.getString("link");
            System.out.println(url);
            try {
                adapter.addImage(clarifai(url), LoadImageFromWebOperations(url));
            } catch (Exception e) {
                Toast.makeText(getApplicationContext(), "Clarifai API has temporarily gone down!", Toast.LENGTH_SHORT).show();
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private String[] concepts = {"coca cola can", "sprite can", "water bottle", "red bull can", "clementine", "dr pepper can"};

    private String clarifai(String guess) {

        double highestScore = 0;
        String answer = "";

        for (int i = 0; i < concepts.length; i ++) {
            String accessToken = "3tYCWhYXUcUeKpnyqqHaFT4n99h2TW";
            String namespace = "default";

            try {
                URL clarifyUrl = new URL("https://api-alpha.clarifai.com/v1/curator/concepts/" + namespace + "/" + URLEncoder.encode(concepts[i], "UTF-8").replaceAll("\\+", "%20") + "/predict");
                HttpURLConnection conn = (HttpURLConnection) clarifyUrl.openConnection();

//            System.out.println(clarifyUrl);

                String data = "{\"urls\": " + "[\"" + guess + "\"]}";

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

//            System.out.println(data);

                // Get the response
                BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));

//            System.out.println("got connection");

                String line;
                while ((line = rd.readLine()) != null) {
                    stb.append(line).append("\n");
                }
                wr.close();
                rd.close();

//            System.out.println(stb.toString());
                double obj = (double) ((JSONObject) (new JSONObject(stb.toString()).getJSONArray("urls").get(0))).get("score");
                if (obj > highestScore) {
                    highestScore = obj;
                    answer = concepts[i];
                }


            } catch(Exception e) {
                e.printStackTrace();
            }
        }
        urlToConcept.put(guess, answer);
        return answer;
    }

    @Override
    public boolean onPrepareOptionsMenu (Menu menu) {
        return false;
    }

//    @Override
//    public boolean onCreateOptionsMenu(Menu menu) {
//        // Inflate the menu; this adds items to the action bar if it is present.
//        getMenuInflater().inflate(R.menu.menu_main, menu);
//        return true;
//    }

//    @Override
//    public boolean onOptionsItemSelected(MenuItem item) {
//        // Handle action bar item clicks here. The action bar will
//        // automatically handle clicks on the Home/Up button, so long
//        // as you specify a parent activity in AndroidManifest.xml.
//        int id = item.getItemId();
//
//        //noinspection SimplifiableIfStatement
//        if (id == R.id.action_settings) {
//            return true;
//        }
//
//        return super.onOptionsItemSelected(item);
//    }
}
