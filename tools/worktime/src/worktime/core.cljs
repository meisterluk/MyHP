(ns meisterluk.worktime
  (:require
    [dommy.core :refer-macros [sel sel1] :as dommy]
    [cljs-time.core :as time]
    [cljs-time.coerce :as timefmt]
    [clojure.string :as str]))

(defn ce [tag & [text]]
  (let [el (dommy/create-element tag)]
    (when text
      (dommy/set-text! el text))
    el))

(defn remove-all-lines! [table]
  (let [first-child (sel1 table :tr)]
    (if (nil? first-child)
      nil
      (do
        (dommy/remove! first-child)
        (remove-all-lines! table)))))

; TODO  shorten
(defn match-to-date-time [matches]
  (let [year (js/parseInt (get matches 1))
        month (js/parseInt (get matches 2))
        day (js/parseInt (get matches 3))
        hour1 (js/parseInt (get matches 4))
        minute1 (js/parseInt (get matches 5))
        hour2 (js/parseInt (get matches 6))
        minute2 (js/parseInt (get matches 7))]
    {:start (time/date-time year month day hour1 minute1 0)
     :end (time/date-time year month day hour2 minute2 0)}))


(defn parse-line [lineno, line]
  (let [pattern (re-pattern #"([0-9]{4})\.([0-9]{2})\.([0-9]{2}) ([0-9]{2}):([0-9]{2})-([0-9]{2}):([0-9]{2}) +(.*)")
        matches (re-matches pattern line)]
    (if (nil? matches)
      {:start nil :end nil :lineno (+ lineno 1) :text line :state :fail}
      (merge (match-to-date-time matches) {:lineno (+ lineno 1) :text (get matches 8) :state :okay}))))

(defn determine-working-hours [content]
  (map-indexed parse-line (str/split-lines content)))

(defn time-diff [dt1 dt2]
  (time/in-minutes (time/interval dt1 dt2)))

(defn process-working-hours [predata]
  (let [f #(assoc % :diff
      (if (= (:state %) :okay)
        (time-diff (:start %) (:end %))
        0))]
    (map f predata)))

(defn daterepr [dt]
  (str (.getUTCDay dt) "-" (.getUTCMonth dt) "-" (.getYear dt) " " (.getMinutes dt) ":" (.getHours dt)))

(defn row-to-element [row]
  (let [tr (dommy/create-element :tr)
        lineno (dommy/create-element :td)
        start (dommy/create-element :td)
        end (dommy/create-element :td)
        desc (dommy/create-element :td)
        diff (dommy/create-element :td)
        success (dommy/create-element :td)]
    (dommy/set-text! lineno (str (:lineno row)))
    (dommy/append! tr lineno)
    (if (= (:state row) :okay)
      (do
        (dommy/set-text! start (daterepr (timefmt/to-local-date-time (:start row))))
        (dommy/set-text! end (daterepr (timefmt/to-local-date-time (:end row))))))
    (dommy/append! tr start)
    (dommy/append! tr end)
    (dommy/set-text! desc (str (:text row 2)))
    (dommy/append! tr desc)
    (if (= (:state row) :okay)
      (do
        (dommy/set-text! diff (str (:diff row)))
        (dommy/set-text! success "OK"))
      (do
        (dommy/set-text! success "FAIL")))
    (dommy/append! tr diff)
    (dommy/append! tr success)
    tr))


(defn add-line! [table row]
  (let [elem (row-to-element row)]
    (dommy/append! table elem)))

(defn add-lines! [table data]
  (let [f (first data)
        r (rest data)]
    (if (not (nil? f))
      (do
        (add-line! table f)
        (add-lines! table r)))))

(defn add-summary! [table data & [t]]
  (let [f (first data)
        r (rest data)
        row (dommy/create-element :tr)
        empty1 (dommy/create-element :td)
        empty2 (dommy/create-element :td)
        summ (dommy/create-element :td)
        total_minutes (dommy/create-element :td)
        empty3 (dommy/create-element :td)
        empty4 (dommy/create-element :td)
        accu_min (if (nil? t) 0 t)]
    (if (nil? f)
      (do
        (dommy/append! row empty1)
        (dommy/append! row empty2)
        (dommy/append! row empty3)
        (dommy/set-text! summ (str "Sum (minutes):"))
        (dommy/append! row summ)
        (dommy/set-text! total_minutes (str accu_min))
        (dommy/append! row total_minutes)
        (dommy/append! row empty4)
        (dommy/append! table row)
        row)
      (add-summary! table r (+ (:diff f) accu_min)))))

(defn update-working-hours! []
  (let [table (sel1 :#lines-table)
        input (dommy/value (sel1 :#input))
        pre (determine-working-hours input)
        data (process-working-hours pre)]
    (remove-all-lines! table)
    (add-lines! table data)
    (add-summary! table data)))

(defn main []
  (do
    (println "Application has started")
    (dommy/listen! (sel1 :#determine) :click update-working-hours!)))

(defn doc-ready-handler []
  (let
    [ready-state (. js/document -readyState)]
    (if (= "complete" ready-state)
      (do (main)))))

(defn on-doc-ready []
  (aset  js/document "onreadystatechange" doc-ready-handler ))

(enable-console-print!)

(on-doc-ready)



;(println (ce :div))

;
