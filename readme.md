# Rate Limiting Animations

Rate limiting animations with [Manim](https://github.com/ManimCommunity/manim/).

## Environment

Be aware that there are some system dependencies. See [Manim doc](https://docs.manim.community/en/stable/installation.html) for more details. 
Python environment is managed by [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) here.

Create the environment from the `environment.yml` file:

```shell
conda env create -f environment.yml
```

Export/save environment:

```shell
conda env export | grep -v "^prefix: " > environment.yml
```

## Rendering

Render videos:

```shell
manim -pql rate_limit_scenes.py FixWindowScene
manim -pql rate_limit_scenes.py SlidingLogScene
manim -pql rate_limit_scenes.py TokenBucketScene
manim -pql rate_limit_scenes.py TokenBucketSceneProlonged
```

Add `--format=gif` to export gif format, i.e.:

```
manim -pql rate_limit_scenes.py FixWindowScene --format=gif
```