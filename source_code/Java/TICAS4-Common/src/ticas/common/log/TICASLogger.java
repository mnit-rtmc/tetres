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
package ticas.common.log;

import ticas.common.config.Config;
import javax.swing.JFrame;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.Logger;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.ConsoleAppender;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.config.Configurator;
import org.apache.logging.log4j.core.config.LoggerConfig;
import org.apache.logging.log4j.core.config.builder.api.AppenderComponentBuilder;
import org.apache.logging.log4j.core.config.builder.api.ConfigurationBuilder;
import org.apache.logging.log4j.core.config.builder.api.ConfigurationBuilderFactory;
import org.apache.logging.log4j.core.config.builder.api.LayoutComponentBuilder;
import org.apache.logging.log4j.core.config.builder.api.RootLoggerComponentBuilder;
import org.apache.logging.log4j.core.config.builder.impl.BuiltConfiguration;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TICASLogger {

    private static LoggerContext context;

    public static void init() {
        Config.init(null);

        ConfigurationBuilder<BuiltConfiguration> builder = ConfigurationBuilderFactory.newConfigurationBuilder();
        builder.setStatusLevel(Level.INFO);
        builder.setConfigurationName("TICAS-Log-Builder");

        AppenderComponentBuilder appenderBuilder = builder.newAppender("Console", "CONSOLE").addAttribute("target", ConsoleAppender.Target.SYSTEM_ERR);
        appenderBuilder.add(builder.newLayout("PatternLayout").addAttribute("pattern", "%d{yyyy-MM-dd HH:mm:ss,SSS} :: %-10t :: %-5p :: %c :: %m %n"));
        builder.add(appenderBuilder);

        LayoutComponentBuilder layoutBuilder = builder.newLayout("PatternLayout")
                .addAttribute("pattern", "%d [%t] %-5level: %msg%n");

        appenderBuilder = builder.newAppender("Rolling", "RollingFile")
                .addAttribute("fileName", "logs/ticas.log")
                .addAttribute("filePattern", "logs/archive/ticas-%d{MM-dd-yy}.log.gz")
                .add(builder.newLayout("PatternLayout").addAttribute("pattern", "%d{yyyy-MM-dd HH:mm:ss,SSS} :: %-10t :: %-5p :: %c :: %m %n"))
                .addComponent(builder.newComponent("DefaultRolloverStrategy").addAttribute("max", "10"))
                .addComponent(builder.newComponent("Policies").addComponent(builder.newComponent("SizeBasedTriggeringPolicy").addAttribute("size", "10M")));

        builder.add(appenderBuilder);

        RootLoggerComponentBuilder rootLogger = builder.newRootLogger(Level.getLevel(Config.getLogLevel()));
        rootLogger.add(builder.newAppenderRef("Rolling"));
        rootLogger.add(builder.newAppenderRef("Console"));
        builder.add(rootLogger);

        context = Configurator.initialize(builder.build());
    }

    public static void setLogLevel(Level level) {
        if (TICASLogger.context == null) {
            TICASLogger.init();
        }        
        Configuration config = context.getConfiguration();
        LoggerConfig loggerConfig = config.getLoggerConfig(LogManager.ROOT_LOGGER_NAME);
        loggerConfig.setLevel(level);
        context.updateLoggers();
    }

    public static Logger getLogger(String name) {
        if (TICASLogger.context == null) {
            TICASLogger.init();
        }
        return TICASLogger.context.getLogger(name);
    }

    private TICASLogger() {
    }
}
