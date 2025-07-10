from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError


class Article(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    preview_image = models.ImageField(null=True, blank=True)
    content = models.TextField()
    show_at_index = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    modified_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "칼럼"
        verbose_name_plural = "칼럼s"

    def __str__(self):
        return f"{self.id} - {self.title}"


class Restaurant(models.Model):
    name = models.CharField("이름", max_length=100, db_index=True)
    branch_name = models.CharField(
        "지점", max_length=100, db_index=True, null=True, blank=True
    )
    description = models.TextField("설명", null=True, blank=True)
    address = models.CharField("주소", max_length=255, db_index=True)
    feature = models.CharField("특징", max_length=255, null=True, blank=True)
    is_closed = models.BooleanField("폐업여부", default=False)
    latitude = models.DecimalField(
        "위도",
        max_digits=16,
        decimal_places=12,
        db_index=True,
        default="0.0000",
    )
    longitude = models.DecimalField(
        "경도",
        max_digits=16,
        decimal_places=12,
        db_index=True,
        default="0.0000",
    )
    phone = models.CharField("전화번호", max_length=16, help_text="E.164 포맷")
    rating = models.DecimalField("평점", max_digits=3, decimal_places=2, default=0.0)
    rating_count = models.PositiveIntegerField("전화번호", default=0)
    start_time = models.TimeField("영업 시작시간", null=True, blank=True)
    end_time = models.TimeField("영업 종료시간", null=True, blank=True)
    last_order_time = models.TimeField("마지막 주문시간", null=True, blank=True)
    category = models.ForeignKey(
        "식당 카테고리", on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField("태그", blank=True)
    region = models.ForeignKey(
        "지역",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="restaurants",  # 역참조 이름 설정
        verbose_name="지역",
    )

    class Meta:
        verbose_name = "레스토랑"
        verbose_name_plural = "레스토랑s"

    def __str__(self):
        return f"{self.name} {self.branch_name}" if self.branch_name else self.name

    # 지점명 있으면 이름 지점명을 반환해주고, 없으면 식당 이름만 반환해주고


class CuisineType(models.Model):
    name = models.CharField("이름", max_length=20)

    class Meta:
        verbose_name = "음식 종류"
        verbose_name_plural = "음식 종류"

    def __str__(self):
        return self.name


class RestaurantCategory(models.Model):
    name = models.CharField("이름", max_length=20)
    cuisine_type = models.ForeignKey(
        "CuisineType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "식당 카테고리"
        verbose_name_plural = "식당 카테고리"

    def __str__(self):
        return self.name


class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    is_representative = models.BooleanField("대표 이미지 여부", default=False)
    order = models.PositiveIntegerField("순서", null=True, blank=True)
    name = models.CharField("이름", max_length=100, null=True, blank=True)
    image = models.ImageField("이미지", max_length=100, upload_to="restaurant")
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "식당 이미지"
        verbose_name_plural = "식당 이미지s"

    def __str__(self):
        return f"{self.id}:{self.image}"

    def clean(self):
        images = self.restaurant.restaurantimage_set.filter(is_representative=True)
        # .restaurantimage_set : 해당 restaurant에 연결된 모든 이미지들
        if self.is_representative and images.exclude(id=self.id).count() > 0:
            # 현재 이미지가 대표이미지이고, 이 외에 다른 이미지가 1개 이상 존재한다면
            raise ValidationError("대표 이미지는 1개만 지정 가능합니다.")  # 막아랏!


class RestaurantMenu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField("이름", max_length=100)
    price = models.PositiveIntegerField("가격", default=0)
    image = models.ImageField(
        "이미지", upload_to="restaurant-menu", null=True, blank=True
    )  # MEDIA_ROOT/restaurant-memu/이미지파일을 저장
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "식당 메뉴"
        verbose_name_plural = "식당 메뉴s"

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.CharField("제목", max_length=100)
    author = models.CharField("작가", max_length=100)
    profile_image = models.ImageField(
        "프로필 이미지", upload_to="review-profile", null=True, blank=True
    )
    content = models.TextField("내용")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # 양의 정수만 허용하는데, 범위는 1~5 (실제 범위는 0 ~ 30,000 이다.)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    social_channel = models.ForeignKey(
        "social_channel", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "식당 후기"
        verbose_name_plural = "식당 후기s"

    def __str__(self):
        return f"{self.author} : {self.title}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    name = models.CharField("후기 이미지 이름", max_length=20)
    image = models.ImageField(
        "후기 이미지", upload_to="review-Image", null=True, blank=True
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "리뷰이미지"
        verbose_name_plural = "리뷰이미지s"

    def str(self):
        return f"{self.id}:{self.image}"


class Social_channel(models.Model):
    name = models.CharField("SNS", max_length=10)

    class Meta:
        verbose_name = "SNS"
        verbose_name_plural = "SNSs"

    def str(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        "이름", max_length=100, unique=True
    )  # 이 필드는 중복을 허용하지 않음

    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그s"

    def str(self):
        return self.name


class Region(models.Model):
    sido = models.CharField("광역시", max_length=20)
    sigungu = models.CharField("시군구", max_length=20)
    eupmyeondong = models.CharField("읍면동", max_length=20)

    class Meta:
        verbose_name = "지역"
        verbose_name_plural = "지역s"
        unique_together = ("sido", "sigungu", "eupmyeondong")

    def str(self):
        return f"{self.sido} {self.sigungu} {self.eupmyeondong}"
