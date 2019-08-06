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
package edu.umn.natsrl.pyticas;

import ticas.common.pyticas.PyTICASServer;
import ticas.common.config.Config;
import static java.lang.Thread.sleep;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;
import static java.lang.Thread.sleep;
import static java.lang.Thread.sleep;
import static java.lang.Thread.sleep;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class PyTICASServerTest {
    
    public PyTICASServerTest() {
    }
    
    @BeforeClass
    public static void setUpClass() {
    }
    
    @AfterClass
    public static void tearDownClass() {
    }
    
    @Before
    public void setUp() {
    }
    
    @After
    public void tearDown() {
    }

    /**
     * Test of run method, of class PyTICASServer.
     */
    @Test
    public void testRun() {
       
        PyTICASServer instance = new PyTICASServer();
        System.err.println(Config.getPythonPath());
        System.err.println(Config.getServerPath());
        instance.run();
        try {
            sleep(5000);
        } catch (InterruptedException ex) {
            Logger.getLogger(PyTICASServerTest.class.getName()).log(Level.SEVERE, null, ex);
        }
        assertTrue(instance.isStarted);
        int code = instance.stopServerSynced();
        assertTrue(code == 200);
    }

//    /**
//     * Test of stopServer method, of class PyTICASServer.
//     */
//    @Test
//    public void testStopServer() {
//        System.out.println("stopServer");
//        PyTICASServer instance = new PyTICASServer();
//        instance.stopServer();
//        // TODO review the generated test code and remove the default call to fail.
//        fail("The test case is a prototype.");
//    }
//
//    /**
//     * Test of finalize method, of class PyTICASServer.
//     */
//    @Test
//    public void testFinalize() throws Exception {
//        try {
//            System.out.println("finalize");
//            PyTICASServer instance = new PyTICASServer();
//            instance.finalize();
//            // TODO review the generated test code and remove the default call to fail.
//            fail("The test case is a prototype.");
//        } catch (Throwable ex) {
//            Logger.getLogger(PyTICASServerTest.class.getName()).log(Level.SEVERE, null, ex);
//        }
//    }
    
}
