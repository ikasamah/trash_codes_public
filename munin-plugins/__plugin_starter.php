#!/usr/bin/env php
<?php

// to get values set in plugin-conf.d
// $_ENV['key'];
if ($argc < 2) {
    print_values();
} elseif ($argv[1] === 'config') {
    print_config();
} elseif ($argv[1] === 'autoconf') {
    print_autoconf();
}
exit();

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
    echo "yes\n";
}

