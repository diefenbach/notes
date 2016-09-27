from __future__ import print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

from taggit.models import Tag

from cba import components
from notes.components.note_view import NoteView
from notes.models import Note


class NoteEdit(components.Group):
    """A component which renders the Note add/edit form.
    """
    def init_components(self):
        tags = components.Select(id="tags", label="Tags", multiple=True)
        self.initial_components = [
            components.HiddenInput(id="note-id"),
            components.TextInput(id="title", label="Title"),
            components.TextArea(id="text", label="Text"),
            tags,
            components.Button(id="save-note", value=_("Save"), css_class="primary", handler="handle_save_note"),
            components.Button(id="cancel", value=_("Cancel"), handler="handle_cancel"),
        ]

        self._load_tags(tags)

    def handle_cancel(self):
        note_view = NoteView(id="note-view")

        note_id = self.get_component("note-id")
        try:
            note = Note.objects.get(pk=note_id.value)
        except Note.DoesNotExist:
            pass
        else:
            note_view.set_current_note(note)

        main = self.get_component("main")
        main.replace_component(
            "note-edit", note_view
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
                self.add_message(_("Note has been modified!"), type="success")
            else:
                # Add a new note
                note = Note.objects.create(title=title.value, text=text.value)
                self.add_message(_("Note has been added!"), type="success")

            # Refresh tags
            note.tags.all().delete()
            if tags.value:
                for value in tags.value:
                    note.tags.add(value)
                note.save()

            # Replace edit view with note display view and select the current
            # added / edited note
            note_view = NoteView(id="note-view")
            note_view.set_current_note(note)

            main = self.get_component("main")
            main.replace_component(
                "note-edit", note_view
            )
            main.refresh()

    def set_note(self, note):
        self._components["note-id"].value = note.id
        self._components["title"].value = note.title
        self._components["text"].value = note.text
        self._components["tags"].value = [tag.name for tag in note.tags.all()]

    def _load_tags(self, select):
        select.options = []
        for tag in Tag.objects.all().order_by("name"):
            select.options.append({
                "name": tag.name,
                "value": tag.name,
            })