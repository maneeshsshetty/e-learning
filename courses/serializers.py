from rest_framework import serializers
from .models import CustomUser, Course, CourseOffering, Enrollment, Payment, CourseContent

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class CourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = ['id', 'title', 'video', 'file', 'link', 'created_at']

class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    user_has_paid = serializers.SerializerMethodField()
    photo_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'teacher_name', 'teacher_count', 'photo', 'price', 'is_free', 'formatted_price', 'user_has_paid', 'created_at', 'photo_file']
        read_only_fields = ['teacher', 'created_at']

    def get_photo(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def get_teacher_count(self, obj):
        teacher_ids = set()
        if obj.teacher_id:
            teacher_ids.add(obj.teacher_id)
        try:
            offering_teacher_ids = obj.offerings.values_list('teacher_id', flat=True)
            teacher_ids.update(offering_teacher_ids)
        except Exception:
            pass 
            
        return len(teacher_ids)

    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.username
        return None
    
    def get_formatted_price(self, obj):
        """Return formatted price with rupee symbol"""
        if obj.is_free:
            return "FREE"
        return f"₹{obj.price:,.2f}"
    
    def get_user_has_paid(self, obj):
        """Check if current user has paid for this course"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Payment.objects.filter(
                student=request.user,
                course=obj,
                status='success'
            ).exists()
        return False

    def create(self, validated_data):
        photo_file = validated_data.pop('photo_file', None)
        course = Course.objects.create(**validated_data)
        if photo_file:
            course.photo = photo_file
            course.save()
        return course

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.price = validated_data.get('price', instance.price)
        instance.is_free = validated_data.get('is_free', instance.is_free)
        photo_file = validated_data.get('photo_file')
        if photo_file:
            instance.photo = photo_file
        instance.save()
        return instance

class CourseOfferingSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')
    teacher_name = serializers.ReadOnlyField(source='teacher.username')
    quiz_id = serializers.SerializerMethodField()
    contents = CourseContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = CourseOffering
        fields = ['id', 'course', 'course_title', 'teacher', 'teacher_name', 'semester', 'year', 'start_date', 'end_date', 'meet_link', 'class_description', 'quiz_id', 'contents']

    def get_quiz_id(self, obj):
        quiz = obj.quizzes.first()
        return quiz.id if quiz else None

class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course_offering.course.title')
    course_price = serializers.ReadOnlyField(source='course_offering.course.price')
    student_name = serializers.ReadOnlyField(source='student.username')
    
    class Meta:
        model = Payment
        fields = ['id', 'student', 'student_name', 'course_offering', 'course_title', 'course_price', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['student', 'amount', 'status', 'transaction_id', 'created_at']

    def create(self, validated_data):
        import uuid
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        course_offering = validated_data['course_offering']
        amount = course_offering.course.price
        payment = Payment.objects.create(
            student=self.context['request'].user,
            course_offering=course_offering,
            amount=amount,
            payment_method=validated_data['payment_method'],
            status='success',
            transaction_id=transaction_id
        )
        return payment

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    meet_link = serializers.SerializerMethodField()
    class_description = serializers.SerializerMethodField()
    student_name = serializers.ReadOnlyField(source='student.username')
    course_photo = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'course_offering', 'payment', 'enrolled_at', 'grade', 
                  'course_title', 'course_id', 'teacher_name', 'semester', 'year', 'meet_link', 'class_description', 'course_photo']

    def get_offering_safe(self, obj):
        try:
            return obj.course_offering
        except:
            return None

    def get_course_title(self, obj):
        offering = self.get_offering_safe(obj)
        if offering and offering.course:
            return offering.course.title
        return "Unknown Course"

    def get_course_id(self, obj):
        offering = self.get_offering_safe(obj)
        if offering and offering.course:
            return offering.course.id
        return None

    def get_teacher_name(self, obj):
        offering = self.get_offering_safe(obj)
        if offering and offering.teacher:
            return offering.teacher.username
        return None

    def get_semester(self, obj):
        offering = self.get_offering_safe(obj)
        return offering.semester if offering else None

    def get_year(self, obj):
        offering = self.get_offering_safe(obj)
        return offering.year if offering else None

    def get_meet_link(self, obj):
        offering = self.get_offering_safe(obj)
        return offering.meet_link if offering else None

    def get_class_description(self, obj):
        offering = self.get_offering_safe(obj)
        return offering.class_description if offering else None
        
    def get_course_photo(self, obj):
        offering = self.get_offering_safe(obj)
        if offering and offering.course and offering.course.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(offering.course.photo.url)
            return offering.course.photo.url
        return None
