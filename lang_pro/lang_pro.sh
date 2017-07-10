#!/bin/sh
PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
export LANG=ja_JP.UTF-8
/usr/local/bin/php lang_pro.php get_tweet $1
/home/ikesan009/local/lib/python/bin/python3 lang_pro.py $1
/usr/local/bin/php lang_pro.php tweet $1
