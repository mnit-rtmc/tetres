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
package ticas.ticas4;

import ticas.ticas4.ui.SplashDialog;
import ticas.common.config.Config;
import ticas.common.infra.InfraLoader;
import ticas.common.log.TICASLogger;
import ticas.common.plugin.TICASPlugin;
import ticas.common.plugin.TICASPluginOption;
import ticas.common.pyticas.PyTICASServer;
import ticas.ticas4.ui.TICASAboutDialog;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JFrame;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.UIManager;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import ticas.common.ui.IInitializable;
import java.awt.EventQueue;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.io.File;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;
import java.util.Random;
import java.util.Collection;
import net.xeoh.plugins.base.PluginManager;
import net.xeoh.plugins.base.impl.PluginManagerFactory;
import net.xeoh.plugins.base.util.PluginManagerUtil;
import static java.lang.Thread.sleep;
import ticas.common.infra.Infra;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TICASMain extends javax.swing.JFrame {

    public static TICASMain mainFrame;

    private final int DEFAULT_WIDTH = 1200;
    private final int DEFAULT_HEIGHT = 800;
    protected final int initZoom = 10;
    protected final double initLatitude = 44.974878;
    protected final double initLongitude = -93.233414;
    protected final boolean DEV_MODE = true;
    private final List<Integer> initializedTabs = new ArrayList<Integer>();
    private final Random rand = new Random();
    private SplashDialog splash;
    protected int nTryLoadInfra = 0;
    protected PluginManager pm;
    protected PyTICASServer server;
    protected TICASPluginOption ticasPluginOption;

    /**
     * Creates new form MainFrame
     */
    public TICASMain() {

        Config.USE_LOCAL_PYTHON_SERVER = false;
        TICASMain.mainFrame = this;
        Config.init(this);

        initComponents();
        
        this.setVisible(false);
        Thread t = new Thread() {
            @Override
            public void run() {
                try {
                    sleep(getRandom(500, 900));
                    if(Config.USE_LOCAL_PYTHON_SERVER) {
                        initializeTICAS();
                    } else {
                        initializeTICASwithRemoteServer();
                    }
                } catch (InterruptedException ex) {
                    Logger.getLogger(TICASMain.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        };
        t.start();
        splash = new SplashDialog(this, true);
        splash.setVisible(true);

    }

    protected int getRandom(int min, int max) {
        return rand.nextInt((max - min) + 1) + min;
    }

    protected void initializeTICAS() throws InterruptedException {

        org.apache.logging.log4j.core.Logger logger = TICASLogger.getLogger(TICASMain.class.getName());

        splash.set("initializing TICAS...", getRandom(5, 15));
        this.setLocationRelativeTo(null);

        sleep(getRandom(500, 900));

        logger.info("try to start local PyTICAS server");
        splash.set("starting local PyTICAS server...", getRandom(20, 30));
        this.startPythonServer();

        sleep(getRandom(500, 900));

        logger.info("try to load roadway network information");
        int prg = getRandom(35, 40);
        splash.set("loading roadway network information...", prg);
        boolean loaded = false;
        for (int i = 0; i < 50; i++) {
            prg += 5;
            splash.set("trying to connect local PyTICAS server...", prg);
            loaded = InfraLoader.load();
            if (loaded) {
                logger.info("loaded");
                break;
            }
            try {
                sleep(getRandom(500, 900));
            } catch (InterruptedException ex) {
                Logger.getLogger(TICASMain.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        if (!loaded) {
            JOptionPane.showMessageDialog(null, "System Exit : Could not connect to PyTICAS Server");
            System.exit(-1);
        }

        splash.set("initializing UI...", getRandom(70, 85));

        this.initializingUI();
    }

    protected void initializeTICASwithRemoteServer() throws InterruptedException {

        org.apache.logging.log4j.core.Logger logger = TICASLogger.getLogger(TICASMain.class.getName());

        splash.set("initializing TICAS...", getRandom(5, 15));
        this.setLocationRelativeTo(null);

        sleep(getRandom(500, 900));

        logger.info("try to load roadway network information");
        int prg = getRandom(35, 40);
        splash.set("loading roadway network information...", prg);
        
        splash.set("trying to connect TICAS server...", prg);
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                InfraLoader.load();
            }
        });
        thread.start();
        
        
        Infra infra = Infra.getInstance();
        
        while(true) {
            prg += 5;
                
            splash.set("loading roadway network information...", prg);
            if (infra.isInfraReady()) {
                logger.info("loaded");
                break;
            }
            if (infra.isFailToLoadInfra()) {
                JOptionPane.showMessageDialog(null, "System Exit : Could not connect to TICAS server");
                System.exit(-1);
            }

            try {
                sleep(getRandom(500, 900));
            } catch (InterruptedException ex) {
                TICASLogger.getLogger(TICASMain.class.getName()).fatal("error", ex);
            }
            
            if(prg >= 90) {
                prg = getRandom(40, 70);      
            }
        }

        splash.set("initializing UI...", getRandom(70, 95));
        this.initializingUI();
    }
    
    private void initializingUI() {
        try {
            sleep(100);
        } catch (InterruptedException ex) {
            Logger.getLogger(TICASMain.class.getName()).log(Level.SEVERE, null, ex);
        }
        this.tabbedPane.setSelectedIndex(1);
        this.tabDataExtraction.init();

        ChangeListener changeListener = new ChangeListener() {
            @Override
            public void stateChanged(ChangeEvent changeEvent) {
                Integer idx = tabbedPane.getSelectedIndex();
                if (initializedTabs.contains(idx)) {
                    return;
                }
                initializedTabs.add(idx);
                IInitializable tab = (IInitializable) tabbedPane.getSelectedComponent();
                tab.init();
            }
        };
        this.tabbedPane.addChangeListener(changeListener);

        splash.set("loading plugins...", getRandom(90, 98));
        try {
            sleep(getRandom(500, 900));
        } catch (InterruptedException ex) {
            Logger.getLogger(TICASMain.class.getName()).log(Level.SEVERE, null, ex);
        }
        final TICASMain mainWindow = this;
        loadPlugins(new TICASPluginOption() {

            @Override
            public void addTopMenu(JMenuItem menuItem) {
                menuPlugin.add(menuItem);
            }

            @Override
            public void addTabPanel(String tabLabel, JPanel panel) {
                tabbedPane.addTab(tabLabel, panel);
            }

            @Override
            public JFrame getMainWindow() {
                return mainWindow;
            }

            @Override
            public void hideMainWindow() {
                mainWindow.setVisible(false);
            }

            @Override
            public void showMainWindow() {
                mainWindow.setVisible(true);
            }
        });
        splash.dispose();
        this.setSize(DEFAULT_WIDTH, DEFAULT_HEIGHT);
        this.setVisible(true);

        this.addComponentListener(new ComponentListener() {

            @Override
            public void componentResized(ComponentEvent e) {
                EventQueue.invokeLater(new Runnable() {
                    @Override
                    public void run() {
                        scrollPane.revalidate();
                        scrollPane.repaint();
                        mainFrame.revalidate();
                        mainFrame.repaint();
                    }
                });
            }

            @Override
            public void componentMoved(ComponentEvent e) {
            }

            @Override
            public void componentShown(ComponentEvent e) {
            }

            @Override
            public void componentHidden(ComponentEvent e) {
            }
        });
        
    }

    protected void startPythonServer() {
        this.server = new PyTICASServer();
        this.server.setDaemon(true);
        this.server.start();
    }

    protected void loadPlugins(TICASPluginOption ticasOption) {

        org.apache.logging.log4j.core.Logger logger = TICASLogger.getLogger(TICASMain.class.getName());
        logger.info("loading plugins");

        this.ticasPluginOption = ticasOption;
        this.pm = PluginManagerFactory.createPluginManager();
        this.pm.addPluginsFrom(new File("plugins").toURI(), this.ticasPluginOption);

        PluginManagerUtil pmu = new PluginManagerUtil(this.pm);
        final Collection<TICASPlugin> plugins = pmu.getPlugins(TICASPlugin.class);

        for (final TICASPlugin s : plugins) {
            logger.info(String.format("adding plugin : %s", s.getName()));
            s.run(this.ticasPluginOption);
        }
        logger.info("end of loading plugins");
    }

    private void checkClose() {
        if (Config.getTerminateServerOnExit()) {
            server.stopServer();
        }
        System.exit(0);
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        statusPanel1 = new ticas.ticas4.ui.StatusPanel();
        scrollPane = new javax.swing.JScrollPane();
        tabbedPane = new javax.swing.JTabbedPane();
        tabRoute = new ticas.ticas4.TabRoute();
        tabDataExtraction = new ticas.ticas4.TabMOE();
        menubarMain = new javax.swing.JMenuBar();
        menuFile = new javax.swing.JMenu();
        jMenuItem1 = new javax.swing.JMenuItem();
        menuTools = new javax.swing.JMenu();
        menuItemPreferences = new javax.swing.JMenuItem();
        menuItemResetSize = new javax.swing.JMenuItem();
        menuPlugin = new javax.swing.JMenu();
        menuHelp = new javax.swing.JMenu();
        menuItemAbout = new javax.swing.JMenuItem();

        setDefaultCloseOperation(javax.swing.WindowConstants.DO_NOTHING_ON_CLOSE);
        setTitle("Traffic Information and Condition Analysis System");
        setSize(new java.awt.Dimension(1200, 750));
        addWindowListener(new java.awt.event.WindowAdapter() {
            public void windowClosing(java.awt.event.WindowEvent evt) {
                formWindowClosing(evt);
            }
        });

        scrollPane.setBorder(null);

        tabbedPane.addTab("Route", tabRoute);
        tabbedPane.addTab("Data Extraction", tabDataExtraction);

        scrollPane.setViewportView(tabbedPane);

        menuFile.setText("File");
        menuFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                menuFileActionPerformed(evt);
            }
        });

        jMenuItem1.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_Q, java.awt.event.InputEvent.CTRL_MASK));
        jMenuItem1.setText("Quit");
        jMenuItem1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem1ActionPerformed(evt);
            }
        });
        menuFile.add(jMenuItem1);

        menubarMain.add(menuFile);

        menuTools.setText("Tools");

        menuItemPreferences.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_P, java.awt.event.InputEvent.CTRL_MASK));
        menuItemPreferences.setText("Settings");
        menuItemPreferences.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                menuItemPreferencesActionPerformed(evt);
            }
        });
        menuTools.add(menuItemPreferences);

        menuItemResetSize.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_R, java.awt.event.InputEvent.CTRL_MASK));
        menuItemResetSize.setText("Reset Size");
        menuItemResetSize.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                menuItemResetSizeActionPerformed(evt);
            }
        });
        menuTools.add(menuItemResetSize);

        menubarMain.add(menuTools);

        menuPlugin.setText("Plugin");
        menubarMain.add(menuPlugin);

        menuHelp.setText("Help");

        menuItemAbout.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_A, java.awt.event.InputEvent.CTRL_MASK));
        menuItemAbout.setText("About");
        menuItemAbout.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                menuItemAboutActionPerformed(evt);
            }
        });
        menuHelp.add(menuItemAbout);

        menubarMain.add(menuHelp);

        setJMenuBar(menubarMain);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(statusPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, 1060, Short.MAX_VALUE)
                    .addComponent(scrollPane))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(scrollPane, javax.swing.GroupLayout.DEFAULT_SIZE, 541, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(statusPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void formWindowClosing(java.awt.event.WindowEvent evt) {//GEN-FIRST:event_formWindowClosing
        checkClose();
    }//GEN-LAST:event_formWindowClosing

    private void menuItemAboutActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_menuItemAboutActionPerformed
        TICASAboutDialog aboutDialog = new TICASAboutDialog(TICASMain.mainFrame, true);
        aboutDialog.setVisible(true);
    }//GEN-LAST:event_menuItemAboutActionPerformed

    private void jMenuItem1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem1ActionPerformed
        checkClose();
    }//GEN-LAST:event_jMenuItem1ActionPerformed

    private void menuItemPreferencesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_menuItemPreferencesActionPerformed
        Config.showDialog(this);
    }//GEN-LAST:event_menuItemPreferencesActionPerformed

    private void menuFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_menuFileActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_menuFileActionPerformed

    private void menuItemResetSizeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_menuItemResetSizeActionPerformed
        this.setSize(DEFAULT_WIDTH, DEFAULT_HEIGHT);
        this.setLocationRelativeTo(null);
    }//GEN-LAST:event_menuItemResetSizeActionPerformed

    /**
     * @param args the command line arguments
     */
    public static void main(String args[]) {
        /* Set the Nimbus look and feel */
        //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
        /* If Nimbus (introduced in Java SE 6) is not available, stay with the default look and feel.
         * For details see http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html 
         */
        try {
            UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
        } catch (Exception e) {
            java.util.logging.Logger.getLogger("root").info("Windows Look and Feel isn't available");
        }
        //</editor-fold>

        final TICASMain ticasMain = new TICASMain();
//        
//        Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {
//            public void run() {
//                ticasMain.server.stopServer();
//            }
//        }, "Shutdown-thread"));        
//        
        /* Create and display the form */
        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                ticasMain.setVisible(true);
            }
        });

    }

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JMenuItem jMenuItem1;
    private javax.swing.JMenu menuFile;
    private javax.swing.JMenu menuHelp;
    private javax.swing.JMenuItem menuItemAbout;
    private javax.swing.JMenuItem menuItemPreferences;
    private javax.swing.JMenuItem menuItemResetSize;
    private javax.swing.JMenu menuPlugin;
    private javax.swing.JMenu menuTools;
    private javax.swing.JMenuBar menubarMain;
    private javax.swing.JScrollPane scrollPane;
    private ticas.ticas4.ui.StatusPanel statusPanel1;
    private ticas.ticas4.TabMOE tabDataExtraction;
    private ticas.ticas4.TabRoute tabRoute;
    private javax.swing.JTabbedPane tabbedPane;
    // End of variables declaration//GEN-END:variables

}
