(ns meisterluk.worktime
  (:require
    [dommy.core :refer-macros [sel sel1] :as dommy]
    [cljs-time.core :as time]
    [cljs-time.coerce :as timefmt]
    [clojure.string :as str]))

;; worktime
;;
;; Consider a file with a content like the following:
;;
;;    2015.12.20 21:20-22:04      working on worktime clojurescript
;;    2015.12.24 23:24-23:59      christmas time!
;;
;; We want to sum up the minutes passed by in the timedeltas mentioned in this
;; file (22:04–21:20 = 44 minutes, 23:59–23:24 = 35 minutes, sum = 79 minutes).
;; This file generates HTML which visualizes this sum in a table.
;;
;; Public Domain, 2015, Lukas Prokop

;; DOM manipulation

(defn write-total-minutes! [total]
  "Write the number of total minutes to #total"
  (dommy/set-text! (sel1 :#total) (str total)))

(defn remove-all-rows! [table]
  "Given a table, remove all <tr> in <tbody>"
  (let [tbody (sel1 table :tbody)
        trows (sel tbody :tr)]
    (doseq [row trows] dommy/remove!)))

(defn create-element! [tag parent & [text]]
  "Given a tagname symbol, a parent element and optionally a text,
  create a new element of tagname, set its parent and create a subtext node"
  (let [element (dommy/create-element tag)]
    (if (some? text) (dommy/set-text! element text))
    (dommy/append! parent element)
    element))

(defn create-row! [table line]
  "Given a map with line data. Return a <tr> element filled with this data"
  (let [tr (create-element! :tr table)]
    (create-element! :td tr (str (:lineno line)))
    (create-element! :td tr (if (= (:state line) :okay) (str (:start-local line)) ""))
    (create-element! :td tr (if (= (:state line) :okay) (str (:end-local line)) ""))
    (create-element! :td tr (str (:text line)))
    (create-element! :td tr (str (:delta line)))
    (create-element! :td tr (if (= (:state line) :okay) "OK" "FAIL"))
    tr))

(defn add-line! [table line]
  "Given a map with line data. Add the data as <tr> to the given table"
  (let [tbody (sel1 table :tbody)
        elem (create-row! table line)]
    (dommy/append! tbody elem)))

(defn add-lines! [table lines]
  "Given maps with lines data. Add these data as <tr> to the given table"
  (doseq [line lines] (add-line! table line)))


;; Parsing

(def line-regex
  "Regular expression a line must conform to"
  #"([0-9]{4})\.([0-9]{1,2})\.([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2})-([0-9]{1,2}):([0-9]{1,2}) +(.*)")

(defn parse-integers [matches indices]
  "Given a matches vector and a list of indices as strings,
  return the matches elements at those indices in order parsed as integers"
  (map #(js/parseInt (get matches %)) indices))

(defn parse-datetime [matches]
  "Given a match of a line against line-regex, return an object assembling
  the start and end date"
  {:start (apply time/date-time (conj (vec (parse-integers matches [1 2 3 4 5])) 0))
   :end (apply time/date-time (conj (vec (parse-integers matches [1 2 3 6 7])) 0))})

(defn parse-line [lineno line]
  "Given a line string at line number lineno, return a map representing its data"
  (let [pattern line-regex
        matches (re-matches pattern line)]
    (if (nil? matches)
      {:lineno (+ lineno 1) :text line :state :fail}
      (merge (parse-datetime matches) {:lineno (+ lineno 1) :text (get matches 8) :state :okay}))))

(defn parse-lines [content]
  "Given a string with multiple lines, parse each line and return maps
  representing the data of each line"
  (map-indexed parse-line (str/split-lines content)))



;; Data processing

(defn date->str [dt]
  "A string representation for a Javascript Date object"
  (str (.getUTCDay dt) "-" (.getUTCMonth dt) "-" (.getYear dt) " " (.getMinutes dt) ":" (.getHours dt)))

(defn date-time-delta [dt1 dt2]
  "Compute the time delta in minutes between two time/date-time objects"
  (time/in-minutes (time/interval dt1 dt2)))

(defn sum-minutes [data]
  "Compute the sum of minutes of the deltas of all lines"
  (apply + (map #(:delta %) data)))

(defn process-line [line]
  "Given one line of meta data, return an updated line with additional information"
  (if (= (:state line) :okay)
    (assoc line
      :delta (date-time-delta (:start line) (:end line))
      :start-local (date->str (timefmt/to-local-date-time (:start line)))
      :end-local (date->str (timefmt/to-local-date-time (:end line))))
    (assoc line :delta 0 :start-local "" :end-local "")))

(defn process-lines [data]
  "Given lines of data, return a map containing the original and additional data"
  (let [updated (map process-line data)]
    (assoc {} :lines updated :total-minutes (sum-minutes updated))))

(defn update-working-hours! []
  "Read the textarea, parse it, process it and render its results"
  (let [table (sel1 :#lines-table)
        input (dommy/value (sel1 :#input))
        pre (parse-lines input)
        post (process-lines pre)]
    (remove-all-rows! table)
    (add-lines! table (:lines post))
    (write-total-minutes! (:total-minutes post))))


;; Main routine

(defn main []
  "Main routine"
  (println "Application has started")
  (dommy/listen! (sel1 :#determine) :click update-working-hours!))

(defn doc-ready-handler []
  (let [ready-state (. js/document -readyState)]
    (if (= "complete" ready-state)
      (main))))

(defn on-doc-ready []
  (aset js/document "onreadystatechange" doc-ready-handler))

(enable-console-print!)
(on-doc-ready)
