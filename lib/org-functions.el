;;; org-functions.el --- Functions for voice-to-org integration -*- lexical-binding: t -*-

;;; Commentary:
;; Provides functions for creating and modifying org-roam files
;; through external tools like voice-to-org

;;; Code:
(require 'org)
(require 'org-roam)
(require 'org-roam-dailies)

(defvar voice-to-org-debug t
  "Enable debug messages for voice-to-org functions.")

(defun voice-to-org--log (format-string &rest args)
  "Log debug message using FORMAT-STRING and ARGS when debugging is enabled."
  (when voice-to-org-debug
    (let ((message-text (apply #'format format-string args)))
      (with-current-buffer (get-buffer-create "*voice-to-org-debug*")
        (goto-char (point-max))
        (insert (format-time-string "[%Y-%m-%d %H:%M:%S] ")
                message-text "\n"))
      (message "voice-to-org: %s" message-text))))

;;;###autoload
(defun voice-to-org-create-note (title)
  "Create a new org-roam note with TITLE if it doesn't exist.
Returns the path to the note file."
  (voice-to-org--log "Creating new note with title: %s" title)
  (unless (stringp title)
    (error "Title must be a string"))
  (let* ((node (org-roam-node-create :title title))
         (file (org-roam-node-file node))
         (template (list
                   :file file
                   :head (concat
                         ":PROPERTIES:\n"
                         ":ID:       " (org-id-new) "\n"
                         ":END:\n"
                         "#+title: " title "\n\n"))))
    (voice-to-org--log "Note file path: %s" file)
    (unless (file-exists-p file)
      (voice-to-org--log "File doesn't exist, creating...")
      (org-roam-capture- :node node :templates (list template)))
    file))

;;;###autoload
(defun voice-to-org-append-content (file content)
  "Append CONTENT to the specified org-roam FILE."
  (voice-to-org--log "Appending to file: %s" file)
  (voice-to-org--log "Content to append: %s" content)
  (let* ((node-title (file-name-base file))
         (org-roam-capture-templates
          `(("n" "note" plain
             "%?"
             :if-new (file+head "%<%Y%m%d%H%M%S>-${slug}.org"
                               ":PROPERTIES:\n:ID:       %(org-id-new)\n:END:\n#+title: ${title}\n")
             :unnarrowed t))))
    (voice-to-org--log "Finding node with title: %s" node-title)
    (org-roam-node-find node-title)
    (with-current-buffer (current-buffer)
      (voice-to-org--log "Current buffer: %s" (buffer-name))
      (goto-char (point-max))
      (insert (format "\n* %s\n%s" (format-time-string "%Y-%m-%d %H:%M") content))
      (save-buffer))))

;;;###autoload
(defun voice-to-org-daily-capture (content)
  "Add CONTENT to today's daily note using org-roam-dailies."
  (voice-to-org--log "Starting daily capture with content: %s" content)
  (condition-case err
      (let ((org-roam-capture-templates
             '(("d" "daily" plain
                "* %<%H:%M> %?"
                :if-new (file+head "%<%Y-%m-%d>.org"
                                 "#+title: %<%Y-%m-%d>\n")
                :unnarrowed t))))
        (voice-to-org--log "Capturing today's daily note")
        ;; First ensure the daily file exists by finding it
        (org-roam-dailies-find-today)

        ;; Now we're in the buffer for today's daily note
        (voice-to-org--log "Current buffer: %s" (buffer-name))
        (goto-char (point-max))
        (unless (bolp) (insert "\n"))
        (insert (format "* %s\n%s\n"
                       (format-time-string "%H:%M")
                       content))
        (save-buffer)
        (voice-to-org--log "Content added successfully")
        t)  ; Return t to indicate success
    (error
     (voice-to-org--log "Error in daily-capture: %s" (error-message-string err))
     (error "Failed to add content to daily note: %s" err))))

(provide 'org-functions)

;;; org-functions.el ends here

