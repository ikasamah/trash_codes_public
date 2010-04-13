#!/usr/bin/env php
<?
/**
 * 指定時間だけCPUに負荷をかける
 *
 * usage: wastecpu.php 15  # 15秒
 *        wastecpu.php -m 20000  # 20000ミリ秒
 */
define('TICK', 0.025);

$start = microtime(true);
$duration = ($argc > 1) ? (int)array_pop($argv) : 10; // sec
if ($duration <= 0) {
    usage();
}

$opts = getopt("m");
if (isset($opts['m'])) {
    $duration /= 1000;  // to millisecond
}

$end = $start + $duration;
while (($now = microtime(true)) < $end) {
    tick($now);
    $elapse = ($now - $start);
    $pass = ($now - $start) / $duration;
    $len = round(40 * ($pass));
    $progress = (($len > 1) ? str_repeat('=', $len - 1) : '') . '>';
    $fmt = "Y-m-d H:i:s";
    printf("wastecpu.php %8.03f(sec) [%-40s] ETA: %s\r", $elapse, $progress, date($fmt, $end));
}
echo "\n";


function tick($now)
{
    while (microtime(true) < ($now + TICK));
}

function usage()
{
    die("wastecpu.php [-m] TIME\n");
}

