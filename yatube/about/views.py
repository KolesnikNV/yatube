from django.views.generic import TemplateView


class AboutAuthorView(TemplateView):
    """Генирирует author.html."""

    template_name = "about/author.html"

    def get_context_data(self, **kwargs):
        """Передает переменные в шаблон."""

        context = super().get_context_data(**kwargs)
        context["just_title"] = "Об авторе проекта"
        context["just_text"] = (
            " Тут я размещу информацию о себе,"
            "используя свои умения верстать. "
            "Картинки, блоки, элементы бустрап."
        )
        return context


class AboutTechView(TemplateView):
    """Генирирует tech.html."""

    template_name = "about/tech.html"

    def get_context_data(self, **kwargs):
        """Передает переменные в шаблон."""
        context = super().get_context_data(**kwargs)
        context["just_title"] = "Технологии"
        context["just_text"] = "Текст страницы Технологии"
        return context
