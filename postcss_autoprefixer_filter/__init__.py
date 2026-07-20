from django.conf import settings
from compressor.filters import CompilerFilter

COMPRESS_POSTCSS_AUTOPREFIXER_BROWSERSLIST = 'defaults'

class PostCssAutoprefixerFilter(CompilerFilter):
    command = "BROWSERSLIST='{}' npx postcss --use autoprefixer -o {}" . format(
        getattr(settings, "COMPRESS_POSTCSS_AUTOPREFIXER_BROWSERSLIST", COMPRESS_POSTCSS_AUTOPREFIXER_BROWSERSLIST), 
        '{outfile} {infile}'
    )
    