from __future__ import print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

from taggit.models import Tag

from cba import components
from cba import utils

from notes.components.note_display import NoteDisplay
from notes.models import File
from notes.models import Note


class NoteEdit(components.Group):
    """A component which renders the Note add/edit form.
    """
    def init_components(self):
        tags = components.Select(id="tags", label="Tags", multiple=True)
        self.initial_components = [
            components.HiddenInput(id="note-id"),
            components.TextInput(id="title", label=_("Title")),
            components.Textarea(id="text", label=_("Text"), rows=40),
            components.FileInput(
                id="files",
                label=_("Files"),
                icon="file",
                icon_position="right",
                multiple=True,
            ),
            tags,
            components.Button(id="save-note", value=_("Save"), css_class="primary", handler={"click": "server:handle_save_note"}),
            components.Button(id="cancel", value=_("Cancel"), handler={"click": "server:handle_cancel"}),
        ]

        self._load_tags(tags)

    def handle_cancel(self):
        """Handles click on the cancel button.
        """
        note_display = NoteDisplay(id="note-view")

        main = self.get_component("main")
        main.replace_component(
            "note-edit", note_display
        )
        main.refresh()

    def handle_save_note(self):
        request = self.get_request()
        if request.user.is_anonymous():
            self.add_message("Nix!")
            return

        note_id = self.get_component("note-id")
        title = self.get_component("title")
        text = self.get_component("text")
        tags = self.get_component("tags")
        files = self.get_component("files")

        if title.value == "":
            title.error = _("Title is required!")
        else:
            title.error = ""

        if text.value == "":
            text.error = _("Title is required!")
        else:
            text.error = ""

        if title.value == "" or text.value == "":
            self.add_message(_("Please correct the indicated errors!"), type="error")
            title.refresh()
            text.refresh()

        if title.value != "" and text.value != "":
            if note_id.value:
                # Edit an existing note
                note = Note.objects.get(pk=note_id.value)
                note.title = title.value
                note.text = text.value
                note.save()

                # Create files
                for file_value in files.value:
                    File.objects.create(note=note, file=file_value)

                # Delete files
                for to_delete_id in files.to_delete:
                    try:
                        File.objects.get(pk=to_delete_id).delete()
                    except File.DoesNotExist:
                        pass

                self.add_message(_("Note has been modified!"), type="success")
            else:
                # Add a new note
                note = Note.objects.create(title=title.value, text=text.value)
                self.add_message(_("Note has been added!"), type="success")

            # Refresh tags
            note.tags.clear()
            if tags.value:
                for value in tags.value:
                    note.tags.add(value)

            # Replace edit view with note display view and select the current
            # added / edited note
            utils.set_to_session("current-note-id", note.id)
            note_display = NoteDisplay(id="note-view")
            note_display.load_current_note()

            main = self.get_component("main")
            main.replace_component(
                "note-edit", note_display
            )
            main.refresh()

            tag_explorer = self.get_component("tag-explorer")
            tag_explorer.refresh_all()

    def _load_tags(self, select):
        select.options = []
        for tag in Tag.objects.all().order_by("name"):
            select.options.append({
                "name": tag.name,
                "value": tag.name,
            })
