package com.example.jadesym.hackmit;

import android.app.Activity;
import android.content.Context;
import android.graphics.drawable.Drawable;
import android.text.format.Time;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;

import de.hdodenhof.circleimageview.CircleImageView;

public class CustomListAdapter extends ArrayAdapter<String> {

    private final Activity context;
    private final ArrayList<String> itemname;
    private final ArrayList<Drawable> drawList;
    private TextView txtTitle;
    private TextView extratxt;
    private CircleImageView imageView;
    private int currPos = 0;

    public CustomListAdapter(Activity context, ArrayList<String> itemname, ArrayList<Drawable> drawList) {
        super(context, R.layout.list_row, itemname);
        // TODO Auto-generated constructor stub

        this.context=context;
        this.itemname=itemname;
        this.drawList = drawList;
    }

    public String getTime() {
        Date date = Calendar.getInstance().getTime();
        DateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm");
        return formatter.format(date);
    }

    public View getView(int position,View view,ViewGroup parent) {
        LayoutInflater inflater=context.getLayoutInflater();
        View rowView=inflater.inflate(R.layout.list_row, null,true);

        txtTitle = (TextView) rowView.findViewById(R.id.item);
        imageView = (CircleImageView) rowView.findViewById(R.id.icon);
        extratxt = (TextView) rowView.findViewById(R.id.textView1);

        txtTitle.setText(itemname.get(position));
        imageView.setImageDrawable(drawList.get(position));
        extratxt.setText(getTime());
        currPos+= 1;
        return rowView;

    }

    public void addImage(String inStr, Drawable draw) {
        itemname.add(inStr);
        drawList.add(draw);
        this.notifyDataSetChanged();
//        LayoutInflater inflater=context.getLayoutInflater();
//        View rowView=inflater.inflate(R.layout.list_row, null,true);
//        txtTitle = (TextView) rowView.findViewById(R.id.item);
//        imageView = (CircleImageView) rowView.findViewById(R.id.icon);
//        extratxt = (TextView) rowView.findViewById(R.id.textView1);
//        txtTitle.setText(itemname.get(currPos));
//        imageView.setImageDrawable(drawList.get(currPos));
//        extratxt.setText(getTime());
//        currPos += 1;
    }

}