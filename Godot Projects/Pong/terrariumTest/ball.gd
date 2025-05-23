extends CharacterBody2D

@export var speed := 300.0

func _ready():
	reset_ball()

func _physics_process(delta):
	move_and_slide()
	if position.x < 0 or position.x > 640:
		reset_ball()

func reset_ball():
	position = Vector2(320, 240)
	velocity = Vector2(randf_range(-1, 1), randf_range(-0.5, 0.5)).normalized() * speed
	velocity.x = sign(velocity.x) * speed  # Ensure horizontal direction

func _on_body_entered(body):
	velocity = velocity.bounce(get_last_slide_collision().get_normal())
