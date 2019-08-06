/*
 * Copyright (C) 2018 NATSRL @ UMD (University Minnesota Duluth)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package edu.umn.natsrl.ticas.options;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.prefs.BackingStoreException;
import java.util.prefs.InvalidPreferencesFormatException;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;
import java.util.prefs.Preferences;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class PrefTest {

    public PrefTest() {
    }

    public static void main(String args[]) throws BackingStoreException, IOException, InvalidPreferencesFormatException {

        InputStream is = new BufferedInputStream(new FileInputStream("options.xml"));
        Preferences.importPreferences(is);
        is.close();

        Preferences prefsRoot = Preferences.userRoot();
        Preferences myPrefs = prefsRoot.node("PreferenceExample");
        
        print(myPrefs);
        int v = 1;
        
        myPrefs.put("A", "a-"+v);
        myPrefs.put("B", "b-"+v);
        myPrefs.put("C", "c-"+v);

        print(myPrefs);
        
        // Export the node to a file
        myPrefs.exportNode(new FileOutputStream("options.xml"));
    }

    private static void print(Preferences myPrefs) throws BackingStoreException {
        System.out.println("Node's absolute path: " + myPrefs.absolutePath());

        System.out.println("Node's keys: ");
        for (String s : myPrefs.keys()) {
            System.out.println(s);
        }

        System.out.println("Node's name: " + myPrefs.name());
        System.out.println("Node's parent: " + myPrefs.parent());
        System.out.println("NODE: " + myPrefs);

        byte[] bytes = new byte[10];
        myPrefs.putByteArray("myByteArray", bytes); // byte[]
        System.out.println("==========================");
    }
}
