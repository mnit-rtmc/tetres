--create database cad encoding UTF8 lc_collate='en_US.utf8' lc_ctype='en_US.utf8' template template0;
--create database iris encoding UTF8 lc_collate='en_US.utf8' lc_ctype='en_US.utf8' template template0;
--create database tetres encoding UTF8 lc_collate='en_US.utf8' lc_ctype='en_US.utf8' template template0;
--create database cad encoding UTF8 LC_COLLATE "en_US.UTF-8" LC_CTYPE "en_US.UTF-8" template template0;
--create database iris encoding UTF8 LC_COLLATE "en_US.UTF-8" LC_CTYPE "en_US.UTF-8" template template0;
--create database tetres encoding UTF8 LC_COLLATE "en_US.UTF-8" LC_CTYPE "en_US.UTF-8" template template0;

CREATE DATABASE cad WITH ENCODING='UTF8' LC_CTYPE='en_US.UTF-8' LC_COLLATE='en_US.UTF-8' OWNER=postgres TEMPLATE=template0;
CREATE DATABASE iris WITH ENCODING='UTF8' LC_CTYPE='en_US.UTF-8' LC_COLLATE='en_US.UTF-8' OWNER=postgres TEMPLATE=template0;
CREATE DATABASE tetres WITH ENCODING='UTF8' LC_CTYPE='en_US.UTF-8' LC_COLLATE='en_US.UTF-8' OWNER=postgres TEMPLATE=template0;
