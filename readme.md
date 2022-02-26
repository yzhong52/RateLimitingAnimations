# Animations with Manim

Export environment without prefix: https://stackoverflow.com/a/41274348/1035008

```
conda env export | grep -v "^prefix: " > environment.yml
```

Generate animation for rate limiting:

```
manim -pql rate_limit_scenes.py FixWindowScene
manim -pql rate_limit_scenes.py SlidingLogScene
manim -pql rate_limit_scenes.py TokenBucketScene
manim -pql rate_limit_scenes.py TokenBucketSceneProlonged
```

Here is for generating gif:

```
manim -pql rate_limit_scenes.py FixWindowScene --format=gif
manim -pql rate_limit_scenes.py SlidingLogScene --format=gif
manim -pql rate_limit_scenes.py TokenBucketScene --format=gif
manim -pql rate_limit_scenes.py TokenBucketSceneProlonged --format=gif
```