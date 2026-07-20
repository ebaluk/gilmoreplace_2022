import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save, pre_save

from wagtailvideos import get_transcoder_backend, get_video_model
from wagtailvideos.enums import MediaFormats, VideoQuality

logger = logging.getLogger(__name__)


def _start_mp4_transcode(video_id):
    Video = get_video_model()
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return

    backend = get_transcoder_backend()
    if not backend.installed():
        logger.warning("Skipping auto-transcode: transcoder backend is not installed")
        return

    video.do_transcode(MediaFormats.MP4, VideoQuality.HIGHEST)


def _video_file_changed(instance):
    Video = get_video_model()
    if not instance.pk:
        return True
    try:
        previous = Video.objects.get(pk=instance.pk)
    except Video.DoesNotExist:
        return True
    return previous.file.name != instance.file.name


def video_pre_save(sender, instance, **kwargs):
    instance._auto_transcode = _video_file_changed(instance)


def video_post_save(sender, instance, **kwargs):
    if hasattr(instance, "_from_signal"):
        return
    if not getattr(instance, "_auto_transcode", False):
        return
    if getattr(settings, "WAGTAIL_VIDEOS_DISABLE_TRANSCODE", False):
        return

    video_id = instance.pk
    transaction.on_commit(lambda: _start_mp4_transcode(video_id))


def register_signal_handlers():
    Video = get_video_model()
    pre_save.connect(video_pre_save, sender=Video, dispatch_uid="wagtailvideos_autoencode_pre_save")
    post_save.connect(video_post_save, sender=Video, dispatch_uid="wagtailvideos_autoencode_post_save")


register_signal_handlers()
