#!/usr/bin/env php
<?php

// to get values set in plugin-conf.d
// $_ENV['key'];
$arg1 = isset($argv[1]) ? $argv[1] : null;
if ($arg1 === 'config') {
    print_config();
} elseif ($arg1 === 'autoconf') {
    print_autoconf();
} else {
    print_values();
}
exit(0);

function print_values()
{
    echo "current.value 100\n";
    echo "total.value 100\n";
}

function print_config()
{
    echo "graph_category MyPlugin\n";
    echo "graph_title MyPlugin1\n";
    echo "graph_vlabel byte\n";
    //echo "graph_args --base 1024 -l\n";
    echo "graph_info MyPlugin - description here\n";
    echo "current.label current value\n";
    echo "total.label total value\n";
    //echo "total.draw LINE2\n";
}

function print_autoconf()
{
    // print yes if this script runable in this system
    echo "yes\n";
}

