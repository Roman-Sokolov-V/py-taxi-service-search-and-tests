from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from taxi.models import Manufacturer, Car
from taxi.forms import ManufacturerSearchForm, CarSearchForm, DriverSearchForm


class SetUpMixin:
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="test123", license_number="ADF12345"
        )
        self.client.force_login(self.user)
        self.manufacturer = Manufacturer.objects.create(
            name="ZAZ", country="Ukraine"
        )
        self.another_manufacturer = Manufacturer.objects.create(
            name="Mercedes-Benz", country="Germany"
        )


class PublicIndexTests(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:index"))
        self.assertNotEqual(res.status_code, 200)


class PrivateIndexTests(SetUpMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )
        self.car.drivers.add(self.user)
        self.another_car = Car.objects.create(
            model="Mercedes-Benz S-Class",
            manufacturer=self.another_manufacturer,
        )

    def test_login_provided(self):
        res = self.client.get(reverse("taxi:index"))
        self.assertEqual(res.status_code, 200)
        self.assertIn("num_visits", res.context)
        self.assertEqual(
            res.context["num_drivers"], get_user_model().objects.count()
        )
        self.assertEqual(res.context["num_cars"], Car.objects.count())
        self.assertEqual(
            res.context["num_manufacturers"], Manufacturer.objects.count()
        )
        self.assertEqual(res.context["num_visits"], 1)
        res = self.client.get(reverse("taxi:index"))
        self.assertEqual(res.context["num_visits"], 2)
        self.assertTemplateUsed(res, "taxi/index.html")


class PublicManufacturerListViewTests(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:manufacturer-list"))
        self.assertNotEqual(res.status_code, 200)


class PrivateManufacturerListViewTests(SetUpMixin, TestCase):
    def test_retrieve_manufacturer_list(self):
        res = self.client.get(reverse("taxi:manufacturer-list"))
        manufacturer_list = Manufacturer.objects.all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            list(res.context["manufacturer_list"]), list(manufacturer_list)
        )
        self.assertTemplateUsed(res, "taxi/manufacturer_list.html")
        self.assertIn("manufacturer_search_form", res.context)

        response = self.client.get(
            reverse("taxi:manufacturer-list")
            + f"?name={self.manufacturer.name}"
        )
        self.assertEqual(res.status_code, 200)
        form = response.context["manufacturer_search_form"]
        self.assertIsInstance(form, ManufacturerSearchForm)
        self.assertEqual(form.initial["name"], "ZAZ")
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(
                manufacturer_list.filter(
                    name__icontains=self.manufacturer.name
                )
            ),
        )


class PublicManufacturerCreateViewTests(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:manufacturer-create"))
        self.assertNotEqual(res.status_code, 200)


class PrivatManufacturerCreateViewTests(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.post(
            reverse("taxi:manufacturer-create"),
            {"name": "BMW", "country": "Germany"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("taxi:manufacturer-list"))


class PublicManufacturerUpdateView(TestCase):
    def test_login_required(self):
        self.manufacturer = Manufacturer.objects.create(
            name="ZAZ", country="Ukraine"
        )
        res = self.client.get(
            reverse(
                "taxi:manufacturer-update", kwargs={"pk": self.manufacturer.pk}
            )
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateManufacturerUpdateView(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.post(
            reverse(
                "taxi:manufacturer-update", kwargs={"pk": self.manufacturer.pk}
            ),
            {"name": "ZAZ Updated", "country": "Ukraine"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("taxi:manufacturer-list"))


class PublicManufacturerDeleteView(TestCase):
    def test_login_required(self):
        self.manufacturer = Manufacturer.objects.create(
            name="ZAZ", country="Ukraine"
        )
        res = self.client.get(
            reverse(
                "taxi:manufacturer-delete", kwargs={"pk": self.manufacturer.pk}
            )
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateManufacturerDeleteView(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.post(
            reverse(
                "taxi:manufacturer-delete", kwargs={"pk": self.manufacturer.pk}
            ),
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("taxi:manufacturer-list"))


class PublicCarListViewTests(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:car-list"))
        self.assertNotEqual(res.status_code, 200)


class PrivateCarListViewTests(SetUpMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )
        self.another_car = Car.objects.create(
            model="Mercedes-Benz S-Class",
            manufacturer=self.another_manufacturer,
        )

    def test_retrieve_manufacturer_list(self):
        res = self.client.get(reverse("taxi:car-list"))
        car_list = Car.objects.all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context["car_list"]), list(car_list))
        self.assertTemplateUsed(res, "taxi/car_list.html")
        self.assertIn("car_search_form", res.context)

        response = self.client.get(
            reverse("taxi:car-list") + f"?model={self.car.model}"
        )
        self.assertEqual(res.status_code, 200)
        form = response.context["car_search_form"]
        self.assertIsInstance(form, CarSearchForm)
        self.assertEqual(form.initial["model"], self.car.model)
        self.assertEqual(
            list(response.context["car_list"]),
            list(car_list.filter(model__icontains=self.car.model)),
        )


class PublicCarCreateViewTests(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:car-create"))
        self.assertNotEqual(res.status_code, 200)


class PrivateCarCreateViewTests(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.post(
            reverse("taxi:car-create"),
            {
                "model": "ZAZ-1005",
                "manufacturer": f"{self.manufacturer.id}",
                "drivers": [
                    self.user.id,
                ],
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("taxi:car-list"))


class PublicCarUpdateViewTests(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name="ZAZ", country="Ukraine"
        )
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )

    def test_login_required(self):
        res = self.client.get(
            reverse("taxi:car-update", kwargs={"pk": self.car.id})
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateCarUpdateiewTests(SetUpMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )

    def test_login_provided(self):
        res = self.client.get(
            reverse("taxi:car-update", kwargs={"pk": self.car.id})
        )
        self.assertEqual(res.status_code, 200)
        res = self.client.post(
            reverse("taxi:car-update", kwargs={"pk": self.car.id}),
            {
                "model": "ZAZ-1005",
                "manufacturer": f"{self.manufacturer.id}",
                "drivers": [
                    self.user.id,
                ],
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("taxi:car-list"))


class PublicCarDeleteView(TestCase):
    def test_login_required(self):
        self.manufacturer = Manufacturer.objects.create(
            name="ZAZ-1000", country="Ukraine"
        )
        self.car = Car.objects.create(
            model="ZAZ", manufacturer=self.manufacturer
        )
        res = self.client.get(
            reverse("taxi:car-delete", kwargs={"pk": self.car.pk})
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateCarDeleteView(SetUpMixin, TestCase):
    def test_login_provided(self):
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )
        res = self.client.post(
            reverse("taxi:car-delete", kwargs={"pk": self.car.pk}),
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("taxi:car-list"))


class PublicDriverListViewTests(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:driver-list"))
        self.assertNotEqual(res.status_code, 200)


class PrivateDriverListViewTests(SetUpMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.anotheruser = get_user_model().objects.create_user(
            username="test_driver",
            password="test_password",
            license_number="ADF12340",
        )

    def test_retrieve_driver_list(self):
        res = self.client.get(reverse("taxi:driver-list"))
        driver_list = get_user_model().objects.all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context["driver_list"]), list(driver_list))
        self.assertTemplateUsed(res, "taxi/driver_list.html")
        self.assertIn("driver_search_form", res.context)

        response = self.client.get(
            reverse("taxi:driver-list")
            + f"?username={self.anotheruser.username}"
        )
        self.assertEqual(res.status_code, 200)
        form = response.context["driver_search_form"]
        self.assertIsInstance(form, DriverSearchForm)
        self.assertEqual(form.initial["username"], self.anotheruser.username)
        self.assertEqual(
            list(response.context["driver_list"]),
            list(
                driver_list.filter(
                    username__icontains=self.anotheruser.username
                )
            ),
        )


class PublicDriverDetailViewTests(TestCase):
    def test_login_required(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="test123", license_number="ADF12345"
        )
        res = self.client.get(
            reverse("taxi:driver-detail", kwargs={"pk": self.user.pk})
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateDriverDetailViewTests(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.get(
            reverse("taxi:driver-detail", kwargs={"pk": self.user.pk})
        )
        self.assertEqual(res.status_code, 200)


class PublicDriverCreateView(TestCase):
    def test_login_required(self):
        res = self.client.get(reverse("taxi:driver-create"))
        self.assertNotEqual(res.status_code, 200)


class PrivateDriverCreateView(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.get(reverse("taxi:driver-create"))
        self.assertEqual(res.status_code, 200)


class PublicDriverLicenseUpdateViewTests(TestCase):
    def test_login_required(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="test123", license_number="ADF12345"
        )
        res = self.client.get(
            reverse("taxi:driver-update", kwargs={"pk": self.user.pk})
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateDriverLicenseUpdateViewTests(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.get(
            reverse("taxi:driver-update", kwargs={"pk": self.user.pk})
        )
        self.assertEqual(res.status_code, 200)
        res = self.client.post(
            reverse("taxi:driver-update", kwargs={"pk": self.user.pk}),
            {"license_number": "ABC12345"},
        )
        self.assertEqual(res.status_code, 302)


class PublicDeleteView(TestCase):
    def test_login_required(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="test123", license_number="ADF12345"
        )
        res = self.client.get(
            reverse("taxi:driver-delete", kwargs={"pk": self.user.pk})
        )
        self.assertNotEqual(res.status_code, 200)


class PrivateDeleteViewTests(SetUpMixin, TestCase):
    def test_login_provided(self):
        res = self.client.get(
            reverse("taxi:driver-delete", kwargs={"pk": self.user.pk}),
        )
        self.assertEqual(res.status_code, 200)
        res = self.client.post(
            reverse("taxi:driver-delete", kwargs={"pk": self.user.pk}),
        )
        self.assertEqual(res.status_code, 302)


class PublicToggleAssignToCar(TestCase):
    def test_login_required(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="test123", license_number="ADF12345"
        )
        self.manufacturer = Manufacturer.objects.create(
            name="ZAZ", country="Ukraine"
        )
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )

        res = self.client.get(
            reverse("taxi:toggle-car-assign", kwargs={"pk": self.car.pk})
        )
        self.assertRedirects(
            res,
            (
                reverse("login")
                + "?next="
                + reverse("taxi:toggle-car-assign", kwargs={"pk": self.car.pk})
            ),
        )


class PrivateToggleAssignToCar(SetUpMixin, TestCase):
    def test_login_provided(self):
        self.car = Car.objects.create(
            model="ZAZ-1000", manufacturer=self.manufacturer
        )
        res = self.client.get(
            reverse("taxi:toggle-car-assign", kwargs={"pk": self.car.pk})
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(
            res, reverse("taxi:car-detail", kwargs={"pk": self.car.pk})
        )
        self.assertIn(self.user, self.car.drivers.all())
        res = self.client.get(
            reverse("taxi:toggle-car-assign", kwargs={"pk": self.car.pk})
        )
        self.assertNotIn(self.user, self.car.drivers.all())
