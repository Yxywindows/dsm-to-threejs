import React from 'react';
import {AbsoluteFill, Audio, Composition, OffthreadVideo, registerRoot, Series, staticFile} from 'remotion';
import config from '../film.json';
import {validate} from './config.mjs';

const duration = validate(config);
const [vertical, horizontal] = (config.titlePosition ?? 'bottom-right').split('-');
function Film() {
  return <AbsoluteFill style={{backgroundColor: 'black'}}>
    <Series>{config.shots.map((shot, i) => <Series.Sequence key={i} durationInFrames={shot.frames}>
      <OffthreadVideo muted src={staticFile(shot.file)} style={{width:'100%', height:'100%', objectFit:'cover'}}/>
      {i === 0 && config.title && <div style={{position:'absolute',[vertical]:'8%',[horizontal]:'6%',maxWidth:'82%',color:'white', fontFamily:'sans-serif',fontWeight:650,fontSize:config.height * .075,textAlign:horizontal,textShadow:'0 2px 10px #181818'}}>{config.title}</div>}
    </Series.Sequence>)}</Series>
    {config.music && <Audio src={staticFile(config.music)}/>}
  </AbsoluteFill>;
}
function Root() {
  return <Composition id="Film" component={Film} width={config.width} height={config.height} fps={config.fps} durationInFrames={duration}/>;
}
registerRoot(Root);
