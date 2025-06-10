import os
import django

# 1. Thiết lập môi trường Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

from products.models import Category

def create_parent_categories():
    """
    Tạo bốn category cha “Áo nam”, “Quần nam”, “Áo nữ”, “Quần nữ”
    nếu chúng chưa tồn tại.
    """
    parents = {}
    for name in ["Áo nam", "Quần nam", "Áo nữ", "Quần nữ"]:
        cat, _ = Category.objects.get_or_create(
            name=name,
            defaults={"description": f"Parent category: {name}"}
        )
        parents[name] = cat
    return parents

def assign_children(parents):
    """
    Gán các category con hiện tại dựa vào mapping rõ ràng:
      - “Áo nam”: những category áo dành cho nam
      - “Áo nữ”: những category áo dành cho nữ
      - “Quần nam”: những category quần dành cho nam
      - “Quần nữ”: những category quần/chân váy/dầm dành cho nữ
    """
    # List tất cả category đang chưa có parent
    qs = Category.objects.filter(parent__isnull=True).exclude(name__in=parents.keys())

    # Mapping cụ thể bằng exact name
    mapping = {
        "Chân váy": "Quần nữ",
        "Đầm Nữ": "Quần nữ",
        "Jeans": "Quần nam",
        "Quần dài và quần bó": "Quần nam",
        "Quần jean nam": "Quần nam",
        "Quần short": "Quần nam",
        "Đồ bơi nam": "Quần nam",
        "Áo hoodie nam": "Áo nam",
        "Áo Len và áo cardigan nam": "Áo nam",
        "Đồ vest nam": "Áo nam",
        "Áo form dài": "Áo nữ",
        "Áo hai dây": "Áo nữ",
        "Áo khoác": "Áo nữ",
        "Áo len và áo cardigan": "Áo nữ",
        "Áo sơ mi": "Áo nữ",
        "Áo thun": "Áo nữ",
    }

    for cat in qs:
        parent_name = mapping.get(cat.name)
        if parent_name:
            cat.parent = parents[parent_name]
            cat.save()
            print(f"Gán '{cat.name}' → parent '{parent_name}'")
        else:
            # Những category không khớp mapping sẽ được bỏ qua
            print(f"Bỏ qua (chưa map) '{cat.name}'")

if __name__ == "__main__":
    parents = create_parent_categories()
    assign_children(parents)
    print("Hoàn tất cập nhật parent–child cho Category.")
