from django.contrib import admin

from .models import (
    Article,
    Restaurant,
    RestaurantCategory,
    RestaurantImage,
    RestaurantMenu,
    Review,
    ReviewImage,
    Socialchannel,
    Tag,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [  # admin페이지에 로그인해서 article목록을 보면 list_display필드가 보인다.
        # 용량이 큰 preview_image와 길이가 긴 content는 상세 페이지에서 설정하도록 여기에 넣지 않음.
        "id",
        "title",
        "show_at_index",
        "is_published",
        "created_at",
        "modified_at",
    ]

    fields = ["title", "preview_image", "content", "show_at_index", "is_published"]
    # 상세페이지에서 수정 가능한 fields (자동으로 생성되는 created_at와 modified_at은 굳이..)
    search_fields = ["title"]
    # title로 article 검색할 수 있음
    list_filter = ["show_at_index", "is_published"]
    # 필터 항목에 공개할지말지(show_at_index), 발행할지말지(is_published) 설정
    date_hierarchy = "created_at"
    # 생성일을 기준으로 연도/월/일/ 내비게이션 링크 생성. (date_hierarchy은 단일 필드만 설정할 수 있는 속성이라서, list에 담지 않는다. )

    actions = ["make_published"]

    # 동작(액션)을 담는 actions변수.
    @admin.action(description="선택한 컬럼을 공개상태로 변경합니다.")
    def make_published(
        self, request, queryset
    ):  # query : 관리자가 선택한 article들의 모음
        queryset.update(is_published=True)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fields = ["name"]
    search_fields = ["name"]


class RestaurantMenuInline(admin.TabularInline):
    model = RestaurantMenu
    extra = 1


class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "branch_name",
        "is_closed",
        "phone",
        "rating",
        "rating_count",
    ]
    fields = [
        "name",
        "branch_name",
        "category",
        "is_closed",
        "phone",
        "latitude",
        "longitude",
        "tags",
    ]
    readonly_fields = ["rating", "rating_count"]
    search_fields = ["name", "branch_name"]
    list_filter = ["tags"]
    autocomplete_fields = ["tags"]
    inlines = [RestaurantMenuInline, RestaurantImageInline]

    # 인스턴스를 생성할때 인라인 표시 안하도록
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []


@admin.register(RestaurantCategory)
class RestaurantCategoryIAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fields = ["cuisine_type", "name"]


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "restaurant_name", "author", "rating", "content_partial"]
    inlines = [ReviewImageInline]

    # 인스턴스를 생성할때 인라인 표시 안하도록
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []

    def restaurant_name(self, obj):
        return obj.restaurant.name

    def content_partial(self, obj):
        return obj.content[:20] + "..." if len(obj.content) > 20 else obj.content


@admin.register(Socialchannel)
class SocialChannelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fields = ["name"]


# -------RestaurantMenu 과 RestaurantImage 은 인라인모델 (속한 모델)
#        Restaurant를 수정할때 설정할 수 있음. 그래서 따로 데코레이터가 필요없음 (reviewimage도 마찬가지) -------
class RestaurantMenuInline(admin.TabularInline):
    model = RestaurantMenu
    extra = 1


class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1
