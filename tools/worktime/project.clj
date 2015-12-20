(defproject meisterluk.worktime "0.1.0-dev"
  :description "Analysis of files logging my working hours"
  :url "http://lukas-prokop.at/proj/worktime"
  :license {:name "Public Domain"
            :url "https://wiki.creativecommons.org/wiki/CC0"}
  :plugins [[lein-cljsbuild "1.1.2"]]
  :cljsbuild {
              :builds [{
                        :source-paths ["src"]
                        :compiler {
                                   :output-to "out/main.js"
                                   ;:source-map true
                                   :optimizations :advanced ;:whitespace
                                   :pretty-print true}}]}
  :dependencies [[org.clojure/clojure "1.7.0"]
                 [org.clojure/clojurescript "1.7.170"]
                 [prismatic/dommy "1.1.0"]
                 [com.andrewmcveigh/cljs-time "0.3.14"]])
