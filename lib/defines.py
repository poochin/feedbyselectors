#!/usr/bin/python
# -*- coding: utf-8 -*-

defaulttesthtml = u'''\
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
        <title>The title</title>
        <link rel="stylesheet" href="main.css" type="text/css"/>
    </head>
    <body>
        <h1>Test Page</h1>
        <nav>
            <ul>
                <li><a href="/index.html">Home</a></li>
                <li><a href="/about.html">About</a></li>
                <li><a href="/download.html">Download</a></li>
            </ul>
        </nav>
        <div id="contain">
            <h2>最新の更新情報</h2>
            <div class="section">
                <h3><a href="/board.php?date=1970-01-01">Hello, World!</a></h3>
                <p class="desc">The Unix epoch time starting.</p>
            </div>
            <div class="section">
                <h3><a href="/board.php?date=1995-09-24">Releasing Windows 95.</a></h3>
                <p class="desc">Microsoft Corp. released Windows95.</p>
            </div>
            <div class="section">
                <h3><a href="/board.php?date=2011-10-04">Publish iPhone 4S</a></h3>
                <p class="desc">Apple Inc. Published iPhone 4S.</p>
            </div>
        </div>
        <footer>
            <address>@poochin</address>
        </footer>
    </body>
</html>
'''

