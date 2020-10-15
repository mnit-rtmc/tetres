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
package user;

import common.config.Config;
import common.infra.Infra;
import common.infra.InfraLoader;
import common.log.TICASLogger;
import common.plugin.TICASPluginOption;
import common.pyticas.PyTICASServer;
import common.util.FileHelper;
import user.panels.operatingconditions.OperatingConditionInfoHelper;
import user.panels.routegroup.RouteGroupInfoHelper;

import javax.swing.*;
import java.util.Random;

import static java.lang.Thread.sleep;

/**
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public final class TeTRESMain extends JFrame {

  protected final int initZoom = 10;
  protected final double initLatitude = 44.974878;
  protected final double initLongitude = -93.233414;
  protected final boolean DEV_MODE = true;
  protected int nTryLoadInfra = 0;
  protected PyTICASServer server;
  protected TICASPluginOption ticasPluginOption;
  protected org.apache.logging.log4j.core.Logger logger;
  private final SplashDialog splash;
  private Random rand = new Random();

  /**
   * Creates new form TTRMSMain
   */
  public TeTRESMain() throws InterruptedException {

    TeTRESConfig.mainFrame = this;
    Config.mainFrame = this;
    Config.USE_LOCAL_PYTHON_SERVER = false;
    TeTRESConfig.init();
    logger = TICASLogger.getLogger(TeTRESMain.class.getName());

    initComponents();

    this.setTitle(this.getTitle() + " - " + TeTRESVersion.version);
    this.setVisible(false);
    Thread t = new Thread() {
      @Override
      public void run() {
        try {
          initializeTeTRES();
        } catch (InterruptedException ex) {
          TICASLogger.getLogger(TeTRESMain.class.getName()).fatal("error", ex);
        }
      }
    };
    t.start();
    splash = new SplashDialog(this, true);
    splash.setVisible(true);
    splash.setTitle("TeTRES");

    this.setVisible(false);
    this.setSize(1600, 800);
    this.setLocationRelativeTo(null);
  }

  protected int getRandom(int min, int max) {
    return rand.nextInt((max - min) + 1) + min;
  }

  protected void initializeTeTRES() throws InterruptedException {
    while (splash == null) {
      sleep(100);
    }

    splash.set("initializing TeTRES...", getRandom(5, 15));
    this.setLocationRelativeTo(null);

    //sleep(getRandom(500, 900));

    logger.info("starting local TeTRES local server");
    splash.set("starting TeTRES local server...", getRandom(20, 30));
    this.startPythonServer();

    //sleep(getRandom(500, 900));

    logger.info("loading roadway network information");
    int prg = getRandom(35, 40);
    splash.set("loading roadway network information...", prg);

    splash.set("trying to connect TeTRES server...", prg);
    Thread thread = new Thread(new Runnable() {
      @Override
      public void run() {
        InfraLoader.load();
      }
    });
    thread.start();

    Infra infra = Infra.getInstance();

    while (true) {
      prg += 5;

      splash.set("loading roadway network information...", prg);
      if (infra.isInfraReady()) {
        logger.info("loaded");
        break;
      }
      if (infra.isFailToLoadInfra()) {
        JOptionPane.showMessageDialog(null, "System Exit : Could not connect to TeTRES server");
        System.exit(-1);
      }

      try {
        sleep(getRandom(500, 900));
      } catch (InterruptedException ex) {
        TICASLogger.getLogger(TeTRESMain.class.getName()).fatal("error", ex);
      }

      if (prg >= 90) {
        prg = getRandom(40, 70);
      }
    }

    splash.set("initializing UI...", getRandom(70, 95));
    panMain.init();

    RouteGroupInfoHelper.importRouteGroups();
    OperatingConditionInfoHelper.importOCs();
    UIHelper.importRequestInfo();


    splash.dispose();
    this.setVisible(true);

  }

  protected void startPythonServer() {
    this.server = new PyTICASServer();
    this.server.setDaemon(true);
    this.server.start();
  }

  private void checkClose() {
    if (Config.getTerminateServerOnExit()) {
      server.stopServer();
    }
    System.exit(0);
  }

  private void openResultFolder() {
    String resultPath = TeTRESConfig.getDataPath(TeTRESConfig.RESULT_DIR_NAME, true);
    FileHelper.openDirectory(resultPath);
  }

  /**
   * This method is called from within the constructor to initialize the form.
   * WARNING: Do NOT modify this code. The content of this method is always
   * regenerated by the Form Editor.
   */
  @SuppressWarnings("unchecked")
  // <editor-fold defaultstate="collapsed" desc="Generated Code">
  private void initComponents() {

    panMain = new TeTRESPanel();
    jMenuBar1 = new JMenuBar();
    menuFile = new JMenu();
    menuItemQuit = new JMenuItem();
    menuTools = new JMenu();
    menuOpenResultFolder = new JMenuItem();
    menuItemOptions = new JMenuItem();
    menuHelp = new JMenu();
    menuItemAbout = new JMenuItem();

    setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
    setTitle("Travel Time Reliability Estimation System Client");
    addWindowListener(new java.awt.event.WindowAdapter() {
      public void windowClosing(java.awt.event.WindowEvent evt) {
        formWindowClosing(evt);
      }
    });

    menuFile.setText("File");

    menuItemQuit.setAccelerator(
        KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_Q, java.awt.event.InputEvent.CTRL_MASK));
    menuItemQuit.setText("Quit");
    menuItemQuit.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        menuItemQuitActionPerformed(evt);
      }
    });
    menuFile.add(menuItemQuit);

    jMenuBar1.add(menuFile);

    menuTools.setText("Tools");

    menuOpenResultFolder.setText("Open Result Folder");
    menuOpenResultFolder.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        menuOpenResultFolderActionPerformed(evt);
      }
    });
    menuTools.add(menuOpenResultFolder);

    menuItemOptions.setAccelerator(
        KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_P, java.awt.event.InputEvent.CTRL_MASK));
    menuItemOptions.setText("Options");
    menuItemOptions.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        menuItemOptionsActionPerformed(evt);
      }
    });
    menuTools.add(menuItemOptions);

    jMenuBar1.add(menuTools);

    menuHelp.setText("Help");

    menuItemAbout.setAccelerator(
        KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_A, java.awt.event.InputEvent.CTRL_MASK));
    menuItemAbout.setText("About");
    menuItemAbout.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        menuItemAboutActionPerformed(evt);
      }
    });
    menuHelp.add(menuItemAbout);

    jMenuBar1.add(menuHelp);

    setJMenuBar(jMenuBar1);

    GroupLayout layout = new GroupLayout(getContentPane());
    getContentPane().setLayout(layout);
    layout.setHorizontalGroup(
        layout.createParallelGroup(GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(panMain, GroupLayout.DEFAULT_SIZE, 1004, Short.MAX_VALUE)
                .addContainerGap())
    );
    layout.setVerticalGroup(
        layout.createParallelGroup(GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(panMain, GroupLayout.DEFAULT_SIZE, 728, Short.MAX_VALUE)
                .addContainerGap())
    );

    pack();
  }

  private void formWindowClosing(java.awt.event.WindowEvent evt) {
    checkClose();
  }

  private void menuItemOptionsActionPerformed(java.awt.event.ActionEvent evt) {
    Config.showDialog(this);
  }

  private void menuItemQuitActionPerformed(java.awt.event.ActionEvent evt) {
    checkClose();
  }

  private void menuItemAboutActionPerformed(java.awt.event.ActionEvent evt) {
    TeTRESAboutDialog aboutDialog = new TeTRESAboutDialog(this, true);
    aboutDialog.setVisible(true);
  }

  private void menuOpenResultFolderActionPerformed(java.awt.event.ActionEvent evt) {
    this.openResultFolder();
  }

  /**
   * @param args the command line arguments
   */
  public static void main(String[] args) {
    System.out.println("> WorkingDir: " + System.getProperty("user.dir"));
    if (args.length > 0) {
      Config.zipURL = args[0];
      System.out.println("> ZipURL: " + args[0]);
    }
    if (args.length > 1) {
      Config.pythonServerURL = args[1];
      System.out.println("> ServerURL: " + args[1]);
    }
    if (Config.zipURL == null || Config.zipURL == ""){
        Config.zipURL = "http://0.0.0.0:5000/tetres/downloaddata";
    }
    if (Config.pythonServerURL == null || Config.pythonServerURL == "") {
        Config.pythonServerURL = "http://0.0.0.0";
    }

    /* Set the Nimbus look and feel */
    //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
    /* If Nimbus (introduced in Java SE 6) is not available, stay with the default look and feel.
     * For details see http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html
     */
    try {
      for (UIManager.LookAndFeelInfo info : UIManager.getInstalledLookAndFeels()) {
        if ("Nimbus".equals(info.getName())) {
          UIManager.setLookAndFeel(info.getClassName());
          break;
        }
      }
    } catch (ClassNotFoundException ex) {
      java.util.logging.Logger.getLogger(TeTRESMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
    } catch (InstantiationException ex) {
      java.util.logging.Logger.getLogger(TeTRESMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
    } catch (IllegalAccessException ex) {
      java.util.logging.Logger.getLogger(TeTRESMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
    } catch (UnsupportedLookAndFeelException ex) {
      java.util.logging.Logger.getLogger(TeTRESMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
    }

    try {
      UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
    } catch (Exception e) {
      java.util.logging.Logger.getLogger("root").info("Windows Look and Feel isn't available");
    }

    /* Create and display the form */
    java.awt.EventQueue.invokeLater(new Runnable() {
      public void run() {
        try {
          new TeTRESMain().setVisible(true);
        } catch (InterruptedException ex) {
          TICASLogger.getLogger(TeTRESMain.class.getName()).fatal("error", ex);
        }
      }
    });
  }

  // Variables declaration - do not modify
  private JMenuBar jMenuBar1;
  private JMenu menuFile;
  private JMenu menuHelp;
  private JMenuItem menuItemAbout;
  private JMenuItem menuItemOptions;
  private JMenuItem menuItemQuit;
  private JMenuItem menuOpenResultFolder;
  private JMenu menuTools;
  private TeTRESPanel panMain;
  // End of variables declaration


}
